# 🛡️ Akamai Identity Audit CLI (v7.1)

A professional CLI tool to audit Akamai API Clients, Permissions, and Credentials.

## 🛠️ Installation & Setup

### 1. Requirements
- **Python 3.8+**
- **Dependencies:** Install via terminal:
  ```bash
  pip install pandas requests akamai-edgegrid
2. Configuration
The script requires an .edgerc file in your home directory (~/.edgerc or C:\Users\<Name>\.edgerc).
Ensure it has [default] credentials with Identity Management: Read-Only access.

🚀 Usage
Standard Run
Bash
python identityscript.py

Export to CSV
Generates two timestamped CSV files (audit_report...csv and metadata_report...csv).

Bash
python akamai_audit.py --export