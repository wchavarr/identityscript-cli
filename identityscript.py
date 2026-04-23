import pandas as pd
import requests
from akamai.edgegrid import EdgeGridAuth
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import argparse
import sys
import datetime

# --- CONFIGURATION ---
BASE_URL = "https://akab-x6dk72mqodpsifbf-7lp2db7eatl5c5at.luna.akamaiapis.net/"
MAX_WORKERS = 15

session = requests.Session()
try:
    session.auth = EdgeGridAuth.from_edgerc("~/.edgerc", section="default")
except Exception as e:
    print(f"Error: Could not find ~/.edgerc file. {e}")
    sys.exit(1)

def get_data(endpoint, switch_key=None):
    params = {'accountSwitchKey': switch_key} if switch_key else {}
    url = urljoin(BASE_URL, endpoint)
    result = session.get(url, params=params)
    result.raise_for_status()
    return result.json()

# --- DATA FETCHING (TAB 1 LOGIC) ---
def fetch_audit_row(client, switch_key):
    client_name = client.get('clientName', 'N/A')
    auth_users = client.get('authorizedUsers', [])
    user = auth_users[0] if auth_users else None
    if not user:
        return [{'API Client': client_name, 'Username': 'N/A', 'API Name': 'N/A', 'Level': 'N/A'}]
    try:
        data = get_data(f"/identity-management/v3/users/{user}/allowed-apis", switch_key)
        if not data:
            return [{'API Client': client_name, 'Username': user, 'API Name': 'NONE', 'Level': 'N/A'}]
        return [{'API Client': client_name, 'Username': user, 'API Name': api.get('apiName', 'N/A'), 'Level': (api.get('accessLevels') or ['N/A'])[0]} for api in data]
    except:
        return [{'API Client': client_name, 'Username': user, 'API Name': 'ERROR', 'Level': 'ERROR'}]

# --- DATA FETCHING (TAB 2 LOGIC) ---
def fetch_credential_row(client, switch_key):
    client_name = client.get('clientName', 'N/A')
    client_id = client.get('clientId', 'N/A')
    client_desc = client.get('clientDescription') or "[No Description]"
    try:
        creds = get_data(f"/identity-management/v3/api-clients/{client_id}/credentials", switch_key)
        if not creds:
            return [{'API Client': client_name, 'Status': 'NO CREDS', 'Created': 'N/A', 'Expires': 'N/A', 'Description': client_desc}]
        
        rows = []
        for c in creds:
            rows.append({
                'API Client': client_name,
                'Status': str(c.get('status', 'UNKNOWN')).upper(),
                'Created': c.get('createdOn', 'N/A'),
                'Expires': c.get('expiresOn', 'N/A'),
                'Description': client_desc
            })
        
        # Deduplication: If ACTIVE exists, only show ACTIVE.
        active_only = [r for r in rows if r['Status'] == 'ACTIVE']
        return active_only if active_only else rows
    except:
        return [{'API Client': client_name, 'Status': 'ERR', 'Created': 'ERR', 'Expires': 'ERR', 'Description': client_desc}]

def main():
    parser = argparse.ArgumentParser(description="Akamai Identity Audit CLI")
    parser.add_argument("--switch", help="Account Switch Key", default=None)
    parser.add_argument("--export", action="store_true", help="Generate two CSV files (audit.csv and metadata.csv)")
    args = parser.parse_args()

    target = args.switch if args.switch else "Primary Account"
    print(f"[*] Connecting to Akamai (Account: {target})...")
    
    try:
        clients = get_data("/identity-management/v3/api-clients", args.switch)
        a_res, c_res = [], []
        
        print(f"[*] Fetching data for {len(clients)} clients using {MAX_WORKERS} workers...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            audit_futures = [ex.submit(fetch_audit_row, c, args.switch) for c in clients]
            cred_futures = [ex.submit(fetch_credential_row, c, args.switch) for c in clients]
            
            for f in audit_futures: a_res.extend(f.result())
            for f in cred_futures: c_res.extend(f.result())

        # Create DataFrames
        df_audit = pd.DataFrame(a_res)
        df_creds = pd.DataFrame(c_res)

        # Output Tab 1 to Terminal
        print("\n" + "="*80)
        print("📊 SECTION 1: PERMISSIONS AUDIT")
        print("="*80)
        print(df_audit.to_string(index=False))

        # Output Tab 2 to Terminal
        print("\n" + "="*80)
        print("📜 SECTION 2: CREDENTIAL METADATA")
        print("="*80)
        print(df_creds.to_string(index=False))

        # Handle CSV Export
        if args.export:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            audit_file = f"audit_report_{ts}.csv"
            meta_file = f"metadata_report_{ts}.csv"
            
            df_audit.to_csv(audit_file, index=False)
            df_creds.to_csv(meta_file, index=False)
            
            print(f"\n[+] Success! CSV files generated:")
            print(f"    - {audit_file}")
            print(f"    - {meta_file}")

        print("\n[+] Audit Process Complete.")

    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()