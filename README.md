# 🛡️ Akamai Identity Audit CLI (v7.2)

A professional Command Line Interface (CLI) tool designed for Akamai administrators to perform rapid security audits of API Clients, User Permissions, and Credential lifecycles.

***

## 📋 Features

* **Permissions Audit:** Maps API Clients to the specific Users and API Names they can access.
* **Credential Metadata:** Tracks status, creation dates, and expiration.
* **Smart Filtering:** Automatically prioritizes the `ACTIVE` credential for each client.
* **Multi-Account Support:** Support for the `--switch` parameter for sub-accounts.
* **Automated Reporting:** Generates timestamped CSV files with the `--export` flag.

***

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. Verify with:

`python --version`

### 2. Install Dependencies
Run the following command to install the required libraries:

`pip install -r requirements.txt`

***

## ⚙️ Configuration

The script requires an **.edgerc** file in your home directory to authenticate.

**1. Create the file:**
* **Windows:** `C:\Users\<YourUsername>\.edgerc`
* **macOS/Linux:** `~/.edgerc`

**2. Add your credentials:**

[default]
client_secret = xxxx
host = xxxx
access_token = xxxx
client_token = xxxx


> **IMPORTANT:** Your API Client must have **Identity Management: Read-Only** access.

***

## 🚀 Usage

Run the script from your terminal using these commands:

**Standard Audit:**
`python identityscript.py`

**Generate CSV Reports:**
`python identityscript.py --export`

***

## 📂 Repository Structure

* `identityscript.py`: The main execution script.
* `requirements.txt`: List of necessary Python libraries.
* `.gitignore`: Prevents private credentials from being uploaded.
* `README.md`: Documentation guide.

***
