🛡️ Akamai Identity Audit CLI (v7.2)
A professional Command Line Interface (CLI) tool designed for Akamai administrators to perform rapid security audits of API Clients, User Permissions, and Credential lifecycles.

📋 Features
Permissions Audit: Maps API Clients to the specific Users and API Names they can access.

Credential Metadata: Tracks status, createdOn, expiresOn, and the clientDescription.

Smart Filtering: If a client has multiple credentials, the tool intelligently prioritizes the ACTIVE one.

Multi-Account Support: Seamlessly switch between accounts/tenants using the Account Switch Key.

Automated Reporting: Generates timestamped CSV files for compliance and offline analysis.

🛠️ Installation
1. Prerequisites
Ensure you have Python 3.8+ installed on your system. You can check this by running:

Bash
python --version
2. Install Dependencies
This project uses pandas for data handling and akamai-edgegrid for secure authentication. Install all requirements using the included requirements.txt file:

Bash
pip install -r requirements.txt
⚙️ Configuration
The script requires an .edgerc file to authenticate with the Akamai APIs.

Create a file named .edgerc in your home directory:

Windows: C:\Users\<YourUsername>\.edgerc

macOS/Linux: ~/.edgerc

Ensure it contains a [default] section with your API tokens:

Plaintext
[default]
client_secret = [YOUR_SECRET]
host = [YOUR_HOST]
access_token = [YOUR_ACCESS_TOKEN]
client_token = [YOUR_CLIENT_TOKEN]
Required Permissions: Your API Client must have at least Identity Management: Read-Only access.

🚀 Usage
Run the script from your terminal using the following commands:

Standard Audit
Displays results directly in your terminal for the primary account.

Bash
python identityscript.py
Audit a Sub-Account (Tenant)
Use the --switch flag to provide a specific Account Switch Key:

Bash
python identityscript.py --switch 1-VJVV:1-2RBL
Generate CSV Reports (Export)
Use the --export flag to print results to the terminal and save two timestamped CSV files (audit_report...csv and metadata_report...csv):

Bash
python identityscript.py --export
📂 Repository Structure
identityscript.py: The main execution script.

requirements.txt: List of necessary Python libraries.

.gitignore: Prevents private credentials from being uploaded to Git.

README.md: This documentation guide.