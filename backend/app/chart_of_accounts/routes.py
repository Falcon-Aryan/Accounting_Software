from flask import jsonify, request
import json
import os
import sys
from typing import Dict, List, Optional
import random
from datetime import datetime
from firebase_admin import auth

from . import chart_of_accounts_bp
from .models import Account, AccountsSummary

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'chart_of_accounts.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Add scripts directory to path for importing
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts')
sys.path.append(SCRIPTS_DIR)

from initialize_accounts import initialize_accounts

def deep_update(original: Dict, update: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def get_user_id():
    """Get the user ID from the Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except:
        return None

def load_accounts(uid: str) -> Dict:
    """Load accounts data from JSON file"""
    try:
        accounts_file = Account.get_user_data_file(uid)
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                accounts_data = json.load(f)
                
                # Check if accounts list is empty
                if len(accounts_data.get('accounts', [])) == 0:
                    # Initialize with default accounts
                    default_file = Account.get_default_accounts_file()
                    if os.path.exists(default_file):
                        with open(default_file, 'r') as f:
                            accounts_data = json.load(f)
                            save_accounts(accounts_data, uid)
                    
                return accounts_data
        else:
            # If user's file doesn't exist, copy from default
            default_file = Account.get_default_accounts_file()
            if os.path.exists(default_file):
                with open(default_file, 'r') as f:
                    accounts_data = json.load(f)
                    save_accounts(accounts_data, uid)
                    return accounts_data
    except Exception as e:
        print(f"Error loading accounts data: {str(e)}")
    return {'accounts': [], 'summary': {}}

def save_accounts(data: Dict, uid: str) -> None:
    """Save accounts data to JSON file"""
    try:
        accounts_file = Account.get_user_data_file(uid)
        os.makedirs(os.path.dirname(accounts_file), exist_ok=True)
        with open(accounts_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving accounts data: {str(e)}")

def load_chart_of_accounts(uid: str) -> Dict:
    """Load chart of accounts data from JSON file"""
    return load_accounts(uid)

def save_chart_of_accounts(data: Dict, uid: str) -> bool:
    """Save chart of accounts data to JSON file"""
    save_accounts(data, uid)
    return True

def update_summary(accounts: List[Dict]) -> AccountsSummary:
    """Update accounts summary information"""
    total = len(accounts)
    active = sum(1 for acc in accounts if acc.get('active', True))
    inactive = total - active
    
    # Calculate total debits and credits based on current balances
    total_debit = sum(
        acc.get('currentBalance', 0) 
        for acc in accounts 
        if acc.get('normalBalanceType') == 'debit' and acc.get('active', True)
    )
    
    total_credit = sum(
        acc.get('currentBalance', 0) 
        for acc in accounts 
        if acc.get('normalBalanceType') == 'credit' and acc.get('active', True)
    )
    
    # Calculate totals by account type
    total_assets = sum(
        acc.get('currentBalance', 0)
        for acc in accounts
        if acc.get('accountType') == 'Asset' and acc.get('active', True)
    )
    
    total_liabilities = sum(
        acc.get('currentBalance', 0)
        for acc in accounts
        if acc.get('accountType') == 'Liability' and acc.get('active', True)
    )
    
    total_equity = sum(
        acc.get('currentBalance', 0)
        for acc in accounts
        if acc.get('accountType') == 'Equity' and acc.get('active', True)
    )
    
    total_income = sum(
        acc.get('currentBalance', 0)
        for acc in accounts
        if acc.get('accountType') == 'Income' and acc.get('active', True)
    )
    
    total_expense = sum(
        acc.get('currentBalance', 0)
        for acc in accounts
        if acc.get('accountType') == 'Expense' and acc.get('active', True)
    )
    
    return AccountsSummary(
        totalAccounts=total,
        activeAccounts=active,
        inactiveAccounts=inactive,
        totalDebit=total_debit,
        totalCredit=total_credit,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=total_equity,
        total_income=total_income,
        total_expense=total_expense,
        last_updated=datetime.utcnow()
    )

def generate_account_id() -> str:
    """Generate a random 8-digit ID with a dash in the middle"""
    first_half = str(random.randint(1000, 9999))
    second_half = str(random.randint(1000, 9999))
    return f"{first_half}-{second_half}"

def is_id_unique(id: str, accounts: List[Dict]) -> bool:
    """Check if an ID is unique among existing accounts"""
    return not any(acc.get('id') == id for acc in accounts)

@chart_of_accounts_bp.route('/create_account', methods=['POST'])
def create_account():
    """Create a new account"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        # Load existing accounts to check ID uniqueness
        accounts_data = load_accounts(uid)
        accounts = accounts_data.get('accounts', [])
        
        # Generate unique ID
        while True:
            new_id = generate_account_id()
            if is_id_unique(new_id, accounts):
                break
        
        # Set the unique ID
        data['id'] = new_id
        
        # Create and validate account
        account = Account.from_dict(data)
        
        # Check for duplicate names
        if any(acc['name'].lower() == account.name.lower() for acc in accounts):
            return jsonify({'error': 'Account with this name already exists'}), 409
        
        # Add new account
        account_dict = account.to_dict()
        accounts.append(account_dict)
        accounts_data['accounts'] = accounts
        accounts_data['summary'] = update_summary(accounts).to_dict()
        
        # Save updated data
        if not save_chart_of_accounts(accounts_data, uid):
            return jsonify({'error': 'Failed to save account'}), 500
        
        return jsonify(account_dict), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/list_accounts', methods=['GET'])
def list_accounts():
    """Get list of all accounts"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    accounts_data = load_accounts(uid)
    return jsonify(accounts_data)

@chart_of_accounts_bp.route('/get/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get account by ID"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = load_accounts(uid)
        accounts = data.get('accounts', [])
        
        account = next((acc for acc in accounts if acc['id'] == account_id), None)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        return jsonify(account), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/update/<account_id>', methods=['PATCH'])
def update_account(account_id):
    """Update an existing account"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        update_data = request.get_json()
        
        # Load existing accounts
        accounts_data = load_accounts(uid)
        accounts = accounts_data.get('accounts', [])
        
        # Find account to update
        account_index = next((i for i, acc in enumerate(accounts) if acc['id'] == account_id), None)
        if account_index is None:
            return jsonify({'error': 'Account not found'}), 404
            
        # Update account
        account = accounts[account_index]
        deep_update(account, update_data)
        
        # Validate updated account
        Account.from_dict(account)  # This will raise ValueError if invalid
        
        # Save changes
        accounts_data['accounts'] = accounts
        accounts_data['summary'] = update_summary(accounts).to_dict()
        if not save_chart_of_accounts(accounts_data, uid):
            return jsonify({'error': 'Failed to save account updates'}), 500
        
        return jsonify(account), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/delete_account/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load data
        data = load_accounts(uid)
        accounts = data.get('accounts', [])
        
        # Find account
        account_index = None
        for i, account in enumerate(accounts):
            if account.get('id') == account_id:
                # Check if account is a default account
                if account.get('isDefault', False):
                    return jsonify({
                        'message': 'Cannot delete default account. You may deactivate it instead.',
                        'error': 'DEFAULT_ACCOUNT'
                    }), 400
                account_index = i
                break
        
        if account_index is None:
            return jsonify({'message': f'Account {account_id} not found'}), 404
            
        # Remove account
        accounts.pop(account_index)
        
        # Update summary
        summary = update_summary(accounts)
        
        # Save changes
        save_accounts({
            'accounts': accounts,
            'summary': summary.to_dict()
        }, uid)
        
        return jsonify({
            'message': f'Account {account_id} deleted successfully',
            'summary': summary.to_dict()
        })
        
    except Exception as e:
        return jsonify({'message': f'Error deleting account: {str(e)}'}), 500

@chart_of_accounts_bp.route('/account_types', methods=['GET'])
def get_account_types():
    """Get list of all valid account types"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        from .models import ACCOUNT_TYPE_DETAILS
        account_types = list(ACCOUNT_TYPE_DETAILS.keys())
        return jsonify(account_types), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/detail-types/<account_type>', methods=['GET'])
def get_detail_types(account_type):
    """Get valid detail types for a given account type"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    from .models import ACCOUNT_TYPE_DETAILS
    
    try:
        if account_type not in ACCOUNT_TYPE_DETAILS:
            return jsonify({'error': 'Invalid account type'}), 400
            
        detail_types = ACCOUNT_TYPE_DETAILS[account_type]
        return jsonify({'detail_types': detail_types}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/accounts_by_type', methods=['GET'])
def get_accounts_by_type():
    """Get accounts grouped by their type"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        accounts_data = load_accounts(uid)
        accounts = accounts_data.get('accounts', [])
        
        # Group accounts by type
        accounts_by_type = {}
        for account in accounts:
            if account.get('active', True):  # Only include active accounts
                acc_type = account.get('accountType')
                if acc_type not in accounts_by_type:
                    accounts_by_type[acc_type] = []
                accounts_by_type[acc_type].append({
                    'id': account.get('id'),
                    'name': account.get('name'),
                    'accountType': account.get('accountType'),
                    'detailType': account.get('detailType'),
                    'description': account.get('description'),
                    'isDefault': account.get('isDefault', False)
                })
        
        return jsonify({
            'accounts_by_type': accounts_by_type,
            'all_accounts': accounts
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@chart_of_accounts_bp.route('/update-balance/<account_id>', methods=['POST'])
def update_account_balance(account_id):
    """Update account balance"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data or 'amount' not in data or 'type' not in data:
            return jsonify({
                'message': 'Amount and type are required'
            }), 400

        amount = float(data['amount'])
        type = data['type']

        # Load accounts
        accounts_data = load_accounts(uid)
        accounts = accounts_data.get('accounts', [])
        
        # Find account
        account_index = None
        for i, acc in enumerate(accounts):
            if acc['id'] == account_id:
                account_index = i
                break
        
        if account_index is None:
            return jsonify({'message': 'Account not found'}), 404
            
        # Update balance
        account = Account.from_dict(accounts[account_index])
        success, error = account.update_balance(amount, type)
        
        if not success:
            return jsonify({'message': error}), 400
            
        # Save changes
        accounts[account_index] = account.to_dict()
        if not save_accounts({'accounts': accounts}, uid):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify(account.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error updating balance: {str(e)}'}), 500

@chart_of_accounts_bp.route('/validate-transaction/<account_id>', methods=['POST'])
def validate_account_transaction(account_id):
    """Validate if a transaction can be applied to an account"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data or 'amount' not in data or 'type' not in data:
            return jsonify({
                'message': 'Amount and type are required'
            }), 400

        amount = float(data['amount'])
        type = data['type']

        # Load accounts
        accounts_data = load_accounts(uid)
        
        # Find account
        account = next(
            (Account.from_dict(acc) for acc in accounts_data.get('accounts', [])
             if acc['id'] == account_id),
            None
        )
        
        if not account:
            return jsonify({'message': 'Account not found'}), 404
            
        # Validate transaction
        is_valid, error = account.validate_transaction(amount, type)
        
        if not is_valid:
            return jsonify({
                'valid': False,
                'message': error
            }), 400
            
        return jsonify({
            'valid': True,
            'balanceChange': account.calculate_balance_change(amount, type)
        })
        
    except Exception as e:
        return jsonify({'message': f'Error validating transaction: {str(e)}'}), 500

@chart_of_accounts_bp.route('/recalculate-balances', methods=['POST'])
def recalculate_balances():
    """Recalculate all account balances from transactions"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load chart of accounts
        chart_data = load_chart_of_accounts(uid)
        accounts = chart_data.get('accounts', [])
        
        # Reset all balances to opening balance
        for account in accounts:
            account['currentBalance'] = account.get('openingBalance', 0.0)
            account['lastTransactionDate'] = None
            
        # Load transactions
        transactions_file = os.path.join(DATA_DIR, uid, 'transactions.json')
        if not os.path.exists(transactions_file):
            transactions_data = {'transactions': []}
        else:
            with open(transactions_file, 'r') as f:
                transactions_data = json.load(f)
                
        transactions = transactions_data.get('transactions', [])
            
        # Process only posted transactions
        posted_transactions = [t for t in transactions if t.get('status') == 'posted']
        posted_transactions.sort(key=lambda x: x.get('date', ''))  # Sort by date
        
        # Update balances from transactions
        for transaction in posted_transactions:
            for entry in transaction.get('entries', []):
                account_id = entry.get('accountId')
                entry_type = entry.get('type')
                amount = float(entry.get('amount', 0))
                
                # Find the account
                account = next((acc for acc in accounts if acc['id'] == account_id), None)
                if account:
                    # Get normal balance type
                    normal_balance = account.get('normalBalanceType', 'debit')
                    current_balance = float(account.get('currentBalance', 0))
                    
                    # Update balance based on entry type and normal balance type
                    if normal_balance == 'debit':
                        # For debit-normal accounts:
                        # Debit increases the balance, Credit decreases it
                        if entry_type == 'debit':
                            account['currentBalance'] = current_balance + amount
                        else:  # credit
                            account['currentBalance'] = current_balance - amount
                    else:  # credit normal
                        # For credit-normal accounts:
                        # Credit increases the balance, Debit decreases it
                        if entry_type == 'credit':
                            account['currentBalance'] = current_balance + amount
                        else:  # debit
                            account['currentBalance'] = current_balance - amount
                            
                    # Update last transaction date
                    account['lastTransactionDate'] = transaction.get('date')
        
        # Calculate totals
        total_assets = 0
        total_liabilities = 0
        total_equity = 0
        total_income = 0
        total_expense = 0
        
        for account in accounts:
            account_type = account.get('accountType', '')
            balance = float(account.get('currentBalance', 0))
            
            if account_type in ['Bank', 'Other Current Asset', 'Fixed Asset', 'Accounts Receivable']:
                total_assets += balance
            elif account_type in ['Credit Card', 'Accounts Payable', 'Other Current Liability', 'Long Term Liability']:
                total_liabilities += balance
            elif account_type == 'Equity':
                total_equity += balance
            elif account_type in ['Income', 'Other Income']:
                total_income += balance
            elif account_type in ['Cost of Goods Sold', 'Expense', 'Other Expense']:
                total_expense += balance
        
        # Update summary
        chart_data['summary'] = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_income': total_income - total_expense,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Save updated chart of accounts
        save_chart_of_accounts(chart_data, uid)
            
        return jsonify({
            'message': 'Account balances recalculated successfully',
            'summary': chart_data['summary']
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error recalculating balances: {str(e)}'}), 500

@chart_of_accounts_bp.route('/normal_balance_types', methods=['GET'])
def get_normal_balance_types():
    """Get normal balance types for all account types"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = load_chart_of_accounts(uid)
        account_types = {}
        
        # Build a mapping of accountType to normalBalanceType
        for account in data['accounts']:
            account_type = account['accountType']
            normal_balance = account['normalBalanceType']
            if account_type not in account_types:
                account_types[account_type] = normal_balance

        return jsonify({
            'normal_balance_types': account_types
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500