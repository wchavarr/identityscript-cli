# 🛡️ Akamai Identity Audit CLI (v7.2)

A professional Command Line Interface (CLI) tool designed for Akamai administrators to perform rapid security audits of API Clients, User Permissions, and Credential lifecycles.

---

## 📋 Features

* **Permissions Audit:** Maps API Clients to the specific Users and API Names they can access.
* **Credential Metadata:** Tracks `status`, `createdOn`, `expiresOn`, and the `clientDescription`.
* **Smart Filtering:** If a client has multiple credentials, the tool intelligently prioritizes the `ACTIVE` one.
* **Multi-Account Support:** Seamlessly switch between accounts/tenants using the Account Switch Key.
* **Automated Reporting:** Generates timestamped CSV files for compliance and offline analysis.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system. Check your version with:
```bash
python --version
2. Install Dependencies
This project requires specific libraries to handle Akamai's authentication and data processing. Install them using:

Bash
pip install -r requirements.txt
⚙️ Configuration
The script requires an .edgerc file to authenticate with Akamai APIs.

Create a file named .edgerc in your home directory:

Windows: C:\Users\<YourUsername>\.edgerc

macOS/Linux: ~/.edgerc

Add your API tokens to a [default] section:

Ini, TOML
[default]
client_secret = [YOUR_SECRET]
host = [YOUR_HOST]
access_token = [YOUR_ACCESS_TOKEN]
client_token = [YOUR_CLIENT_TOKEN]
Note: Your API Client must have Identity Management: Read-Only access or higher.

🚀 Usage
Run the script from your terminal using the following commands:

Standard Audit
Displays results for the primary account defined in your .edgerc.

Bash
python identityscript.py
Audit a Sub-Account (Tenant)
Use the --switch flag to provide a specific Account Switch Key:

Bash
python identityscript.py --switch 1-VJVV:1-2RBL
Generate CSV Reports (Export)
Use the --export flag to print results and save timestamped CSV files:

Bash
python identityscript.py --export
📂 Repository Structure
identityscript.py: The main execution script.

requirements.txt: List of necessary Python libraries.

.gitignore: Prevents private credentials from being uploaded.

README.md: Documentation guide.