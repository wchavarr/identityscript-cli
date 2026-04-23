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

def get_data(endpoint, switch_key=None, params_override=None):
    params = {'accountSwitchKey': switch_key} if switch_key else {}
    if params_override:
        params.update(params_override)
    url = urljoin(BASE_URL, endpoint)
    result = session.get(url, params=params)
    result.raise_for_status()
    return result.json()

# --- DATA FETCHING (TAB 1: CLIENT-CENTRIC PERMISSIONS) ---
def fetch_audit_row(client, switch_key):
    client_name = client.get('clientName', 'N/A')
    client_id = client.get('clientId', 'N/A')
    auth_users = client.get('authorizedUsers', [])
    primary_user = auth_users[0] if auth_users else 'N/A'
    
    try:
        # v7.1 LOGIC: Fetch specific client detail with apiAccess enabled
        data = get_data(f"/identity-management/v3/api-clients/{client_id}", 
                        switch_key, 
                        params_override={"apiAccess": "true"})
        
        api_access_list = data.get('apiAccess', {}).get('apis', [])
        rows = []
        
        if not api_access_list:
            rows.append({
                'API Client': client_name, 
                'Username': primary_user, 
                'API Name': 'NONE / NO ACCESS', 
                'Access Level': 'N/A'
            })
        else:
            for api in api_access_list:
                rows.append({
                    'API Client': client_name, 
                    'Username': primary_user, 
                    'API Name': api.get('apiName', 'N/A'), 
                    'Access Level': api.get('accessLevel', 'N/A')
                })
        return rows
    except Exception:
        return [{'API Client': client_name, 'Username': primary_user, 'API Name': 'ERROR', 'Access Level': 'ERROR'}]

# --- DATA FETCHING (TAB 2: CREDENTIAL METADATA) ---
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
        
        # Deduplication: ACTIVE prioritized, then sorted by Status
        df_temp = pd.DataFrame(rows)
        df_temp['sort_p'] = df_temp['Status'].map({'ACTIVE': 0, 'INACTIVE': 1, 'NO CREDS': 2, 'ERR': 3}).fillna(4)
        df_temp = df_temp.sort_values('sort_p').drop_duplicates(subset=['API Client'], keep='first').drop(columns=['sort_p'])
        return df_temp.to_dict('records')
    except:
        return [{'API Client': client_name, 'Status': 'ERR', 'Created': 'ERR', 'Expires': 'ERR', 'Description': client_desc}]

def main():
    parser = argparse.ArgumentParser(description="Akamai Identity Audit CLI v7.1")
    parser.add_argument("--switch", help="Account Switch Key", default=None)
    parser.add_argument("--export", action="store_true", help="Generate CSV files")
    args = parser.parse_args()

    target = args.switch if args.switch else "Primary Account"
    print(f"[*] Starting Production Audit v7.1")
    print(f"[*] Target: {target}\n")
    
    try:
        # Step 1: List all API clients
        clients = get_data("/identity-management/v3/api-clients", args.switch)
        a_res, c_res = [], []
        
        print(f"[*] Syncing {len(clients)} clients via ThreadPool...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            audit_futures = [ex.submit(fetch_audit_row, c, args.switch) for c in clients]
            cred_futures = [ex.submit(fetch_credential_row, c, args.switch) for c in clients]
            
            for f in audit_futures: a_res.extend(f.result())
            for f in cred_futures: c_res.extend(f.result())

        df_audit = pd.DataFrame(a_res)
        df_creds = pd.DataFrame(c_res)

        # Output Sections
        print("\n" + "="*80 + "\n🔑 SECTION 1: PERMISSIONS AUDIT (Client-Centric)\n" + "="*80)
        print(df_audit.to_string(index=False))

        print("\n" + "="*80 + "\n📜 SECTION 2: CREDENTIAL METADATA\n" + "="*80)
        print(df_creds.to_string(index=False))

        if args.export:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            df_audit.to_csv(f"audit_report_{ts}.csv", index=False)
            df_creds.to_csv(f"metadata_report_{ts}.csv", index=False)
            print(f"\n[+] Reports generated: audit_report_{ts}.csv, metadata_report_{ts}.csv")

        print("\n[+] Audit Process Complete.")

    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()