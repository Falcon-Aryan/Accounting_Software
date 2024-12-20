from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
import random
from datetime import datetime

from . import chart_of_accounts_bp
from .models import Account, AccountsSummary

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'chart_of_accounts.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def deep_update(original: Dict, update: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def load_accounts() -> Dict:
    """Load accounts data from JSON file"""
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading accounts data: {str(e)}")
    return {'accounts': [], 'summary': {}}

def save_accounts(data: Dict) -> bool:
    """Save accounts data to JSON file"""
    try:
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving accounts data: {str(e)}")
        return False

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
    
    return AccountsSummary(
        totalAccounts=total,
        activeAccounts=active,
        inactiveAccounts=inactive,
        totalDebit=total_debit,
        totalCredit=total_credit
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
    try:
        data = request.get_json()
        
        # Load existing accounts to check ID uniqueness
        accounts_data = load_accounts()
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
        if not save_accounts(accounts_data):
            return jsonify({'error': 'Failed to save account'}), 500
        
        return jsonify(account_dict), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/list_accounts', methods=['GET'])
def list_accounts():
    """Get list of all accounts"""
    try:
        accounts_data = load_accounts()
        return jsonify({
            'accounts': accounts_data.get('accounts', []),
            'summary': accounts_data.get('summary', {})
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/get/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get account by ID"""
    try:
        data = load_accounts()
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
    try:
        update_data = request.get_json()
        
        # Load existing accounts
        accounts_data = load_accounts()
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
        if not save_accounts(accounts_data):
            return jsonify({'error': 'Failed to save account updates'}), 500
        
        return jsonify(account), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/delete_account/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    try:
        # Load data
        data = load_accounts()
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
        })
        
        return jsonify({
            'message': f'Account {account_id} deleted successfully',
            'summary': summary.to_dict()
        })
        
    except Exception as e:
        return jsonify({'message': f'Error deleting account: {str(e)}'}), 500

@chart_of_accounts_bp.route('/account_types', methods=['GET'])
def get_account_types():
    """Get list of all valid account types"""
    try:
        from .models import ACCOUNT_TYPE_DETAILS
        account_types = list(ACCOUNT_TYPE_DETAILS.keys())
        return jsonify(account_types), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/detail-types/<account_type>', methods=['GET'])
def get_detail_types(account_type):
    """Get valid detail types for a given account type"""
    print(f"Debug: Received request for account type: {account_type}")
    
    from .models import ACCOUNT_TYPE_DETAILS
    print(f"Debug: Available account types: {list(ACCOUNT_TYPE_DETAILS.keys())}")
    
    try:
        if account_type not in ACCOUNT_TYPE_DETAILS:
            print(f"Debug: Invalid account type: {account_type}")
            return jsonify({'error': 'Invalid account type'}), 400
            
        detail_types = ACCOUNT_TYPE_DETAILS[account_type]
        print(f"Debug: Found detail types: {detail_types}")
        return jsonify({'detail_types': detail_types}), 200
    except Exception as e:
        print(f"Debug: Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/update-balance/<account_id>', methods=['POST'])
def update_account_balance(account_id):
    """Update account balance"""
    try:
        data = request.get_json()
        if not data or 'amount' not in data or 'type' not in data:
            return jsonify({
                'message': 'Amount and type are required'
            }), 400

        amount = float(data['amount'])
        type = data['type']

        # Load accounts
        accounts_data = load_accounts()
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
        if not save_accounts({'accounts': accounts}):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify(account.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error updating balance: {str(e)}'}), 500

@chart_of_accounts_bp.route('/validate-transaction/<account_id>', methods=['POST'])
def validate_account_transaction(account_id):
    """Validate if a transaction can be applied to an account"""
    try:
        data = request.get_json()
        if not data or 'amount' not in data or 'type' not in data:
            return jsonify({
                'message': 'Amount and type are required'
            }), 400

        amount = float(data['amount'])
        type = data['type']

        # Load accounts
        accounts_data = load_accounts()
        
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
