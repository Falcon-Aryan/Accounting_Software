import json
import os
import shutil

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DEFAULT_ACCOUNTS_FILE = os.path.join(DATA_DIR, 'default_accounts.json')
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'chart_of_accounts.json')

def initialize_accounts():
    """Replace the existing chart of accounts with default accounts"""
    try:
        # Make backup of existing accounts
        if os.path.exists(ACCOUNTS_FILE):
            backup_file = ACCOUNTS_FILE + '.backup'
            shutil.copy2(ACCOUNTS_FILE, backup_file)
            print(f"Backup created at: {backup_file}")
        
        # Copy default accounts to chart_of_accounts.json
        shutil.copy2(DEFAULT_ACCOUNTS_FILE, ACCOUNTS_FILE)
        print("Chart of accounts initialized with default accounts")
        
        # Verify the new accounts
        with open(ACCOUNTS_FILE, 'r') as f:
            data = json.load(f)
            print(f"Total accounts created: {len(data['accounts'])}")
            
        return True
    except Exception as e:
        print(f"Error initializing accounts: {str(e)}")
        return False

if __name__ == '__main__':
    initialize_accounts()
