from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import random
from firebase_admin import auth

from . import transactions_bp
from .models import Transaction, TransactionEntry, TransactionType

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CHART_OF_ACCOUNTS_FILE = os.path.join(DATA_DIR, 'chart_of_accounts.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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

def get_default_accounts() -> Dict[str, str]:
    """Get default account IDs from chart of accounts"""
    try:
        uid = get_user_id()
        if not uid:
            return {
                'accounts_receivable': '1100-0001',  # Fallback Accounts Receivable
                'sales_revenue': '4000-0001',        # Fallback Sales Revenue
                'cogs': '5000-0001',                 # Fallback COGS
                'inventory_asset': '1200-0001'       # Fallback Inventory Asset
            }

        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return {
                'accounts_receivable': '1100-0001',  # Fallback Accounts Receivable
                'sales_revenue': '4000-0001',        # Fallback Sales Revenue
                'cogs': '5000-0001',                 # Fallback COGS
                'inventory_asset': '1200-0001'       # Fallback Inventory Asset
            }

        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts = chart_data.get('accounts', [])
            
            # Find default accounts
            accounts_receivable = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Accounts Receivable' 
                and acc['isDefault']), 
                '1100-0001'  # Fallback Accounts Receivable
            )
            
            sales_revenue = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Income' 
                and acc['isDefault']), 
                '4000-0001'  # Fallback Sales Revenue
            )
            
            cogs = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Cost of Goods Sold' 
                and acc['isDefault']), 
                '5000-0001'  # Fallback COGS
            )
            
            inventory_asset = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Other Current Asset' 
                and acc['detailType'] == 'Inventory' 
                and acc['isDefault']), 
                '1200-0001'  # Fallback Inventory Asset
            )
            
            return {
                'accounts_receivable': accounts_receivable,
                'sales_revenue': sales_revenue,
                'cogs': cogs,
                'inventory_asset': inventory_asset
            }
            
    except Exception as e:
        print(f"Error getting default accounts: {str(e)}")
        return {
            'accounts_receivable': '1100-0001',  # Fallback Accounts Receivable
            'sales_revenue': '4000-0001',        # Fallback Sales Revenue
            'cogs': '5000-0001',                 # Fallback COGS
            'inventory_asset': '1200-0001'       # Fallback Inventory Asset
        }

def generate_transaction_id() -> str:
    """Generate a random transaction ID"""
    first_half = str(random.randint(1000, 9999))
    second_half = str(random.randint(1000, 9999))
    return f"{first_half}-{second_half}"

def load_transactions() -> Dict:
    """Load transactions data from JSON file"""
    uid = get_user_id()
    if not uid:
        return {'transactions': []}
    return Transaction.load_user_transactions(uid)

def save_transactions(data: Dict) -> bool:
    """Save transactions data to JSON file"""
    uid = get_user_id()
    if not uid:
        return False
    return Transaction.save_user_transactions(uid, data)

def create_transaction_direct(transaction_data: dict) -> Optional[Dict]:
    """Create a new transaction directly from code (not via HTTP)"""
    try:
        uid = get_user_id()
        if not uid:
            return None

        # Load chart of accounts to get account names
        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts_map = {acc['id']: acc['name'] for acc in chart_data.get('accounts', [])}

        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Set dates
        now = datetime.utcnow().date().isoformat()
        transaction_data['date'] = transaction_data.get('date', now)
        transaction_data['created_at'] = now
        transaction_data['updated_at'] = now
        
        # Add metadata
        transaction_data['id'] = transaction_id
        transaction_data['status'] = transaction_data.get('status', 'draft')
        
        # If entries are not provided, create them
        if not transaction_data.get('entries'):
            # Get transaction details
            amount = float(transaction_data.get('amount', 0.0))  # Ensure float conversion
            description = transaction_data.get('description', 'Transaction')
            
            # Get product info
            products = transaction_data.get('products', [])
            if not products:
                raise ValueError("No products provided for transaction")
                
            product = products[0]  # Get first product
            product_type = product.get('type', 'service')
            
            # Calculate cost amount for inventory items
            cost_amount = 0.0
            if product_type == 'inventory_item':
                # Load products data to get cost price
                with open(os.path.join(DATA_DIR, uid, 'products.json'), 'r') as f:
                    products_data = json.load(f)
                    products_map = {p['id']: p for p in products_data.get('products', [])}
                    
                if product.get('id') in products_map:
                    product_info = products_map[product['id']]
                    cost_price = float(product_info.get('cost_price', 0.0))
                    quantity = float(product.get('quantity', 0.0))
                    cost_amount = cost_price * quantity
            
            # Create entries based on product type
            entries = []
            
            # Revenue entries (common for both types)
            entries.extend([
                {
                    'accountId': get_default_accounts()['accounts_receivable'],
                    'amount': amount,
                    'type': 'debit',
                    'description': f"{description} - Revenue ({accounts_map.get(get_default_accounts()['accounts_receivable'], 'Accounts Receivable')})"
                },
                {
                    'accountId': get_default_accounts()['sales_revenue'],
                    'amount': amount,
                    'type': 'credit',
                    'description': f"{description} - Revenue ({accounts_map.get(get_default_accounts()['sales_revenue'], 'Sales Revenue')})"
                }
            ])
            
            # Add COGS entries for inventory items
            if product_type == 'inventory_item' and cost_amount > 0:
                entries.extend([
                    {
                        'accountId': get_default_accounts()['cogs'],
                        'amount': cost_amount,
                        'type': 'debit',
                        'description': f"{description} - Cost of Goods Sold ({accounts_map.get(get_default_accounts()['cogs'], 'Cost of Goods Sold')})"
                    },
                    {
                        'accountId': get_default_accounts()['inventory_asset'],
                        'amount': cost_amount,
                        'type': 'credit',
                        'description': f"{description} - Inventory Reduction ({accounts_map.get(get_default_accounts()['inventory_asset'], 'Inventory Asset')})"
                    }
                ])
            
            transaction_data['entries'] = entries
        
        # Add account names to entries if not present
        for entry in transaction_data['entries']:
            if not entry.get('accountName'):
                entry['accountName'] = accounts_map.get(entry['accountId'], '')
        
        # Create and validate transaction
        transaction = Transaction.from_dict(transaction_data)
        is_valid, error = transaction.validate()
        if not is_valid:
            raise Exception(error)
        
        # Save transaction
        transactions_data = load_transactions()
        transactions_data['transactions'].append(transaction.to_dict())
        if not save_transactions(transactions_data):
            raise Exception('Failed to save transaction')
        
        # If transaction is posted, update account balances
        if transaction.status == 'posted':
            success, error = update_account_balances(transaction)
            if not success:
                raise Exception(f"Failed to update account balances: {error}")
        
        return transaction.to_dict()
        
    except Exception as e:
        print(f"Error in create_transaction_direct: {str(e)}")
        raise

def validate_transaction_accounts(transaction_type: str, sub_type: str, entries: List[Dict]) -> tuple[bool, str]:
    """Validate if the accounts used in the transaction are appropriate for the transaction type"""
    try:
        uid = get_user_id()
        if not uid:
            return False, "User ID not found"
        
        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return False, "Chart of accounts not found"
        
        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts = {acc['id']: acc for acc in chart_data.get('accounts', [])}
        
        # Verify all accounts exist and are active
        for entry in entries:
            account_id = entry.get('accountId')
            if account_id not in accounts:
                return False, f"Account {account_id} not found"
            if not accounts[account_id].get('active', True):
                return False, f"Account {account_id} is inactive"
        
        # Validate account types based on transaction type
        valid_account_types = get_valid_account_types(transaction_type, sub_type)
        
        for entry in entries:
            account = accounts[entry['accountId']]
            if account['accountType'] not in valid_account_types:
                return False, f"Account type {account['accountType']} is not valid for {transaction_type} transactions"
        
        return True, ""
    except Exception as e:
        return False, str(e)

def get_valid_account_types(transaction_type: str, sub_type: str) -> List[str]:
    """Get valid account types for a transaction type"""
    # All possible account types
    asset_accounts = ['Bank', 'Other Current Asset', 'Fixed Asset', 'Accounts Receivable']
    liability_accounts = ['Credit Card', 'Accounts Payable', 'Other Current Liability', 'Long Term Liability']
    equity_accounts = ['Equity']
    income_accounts = ['Income', 'Other Income']
    expense_accounts = ['Expense', 'Other Expense', 'Cost of Goods Sold']
    
    # Define valid combinations based on accounting principles
    valid_types = {
        'sale': [
            *asset_accounts,      # For receiving payment or recording receivables
            *income_accounts      # For recording revenue
        ],
        'purchase': [
            *asset_accounts,      # For paying or recording assets purchased
            *liability_accounts,  # For recording payment method or payables
            *expense_accounts     # For recording expenses
        ],
        'payment_received': [
            *asset_accounts,      # For recording where payment is received
            'Accounts Receivable' # For clearing the receivable
        ],
        'payment_made': [
            *asset_accounts,      # For recording payment from bank/cash
            *liability_accounts   # For clearing the payable
        ],
        'expense': [
            *asset_accounts,      # For recording payment method
            *liability_accounts,  # For recording payment method
            *expense_accounts     # For recording the expense
        ],
        'equity': [
            *asset_accounts,      # For recording cash/bank accounts
            *liability_accounts,  # For recording credit accounts
            *equity_accounts      # For recording owner's equity
        ],
        'transfer': [
            *asset_accounts,      # For transfers between asset accounts
            *liability_accounts   # For transfers between liability accounts
        ],
        'adjustment': [
            *asset_accounts,      # For adjusting asset values
            *liability_accounts,  # For adjusting liability values
            *equity_accounts,     # For adjusting equity
            *income_accounts,     # For adjusting income
            *expense_accounts     # For adjusting expenses
        ]
    }
    
    return list(set(valid_types.get(transaction_type, [])))  # Remove any duplicates

def update_account_balances(transaction: Transaction) -> tuple[bool, Optional[str]]:
    """Update account balances in the chart of accounts when posting a transaction"""
    try:
        uid = get_user_id()
        if not uid:
            return False, "User ID not found"
        
        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return False, "Chart of accounts not found"
        
        # Load chart of accounts
        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts = chart_data.get('accounts', [])
            
        # Track which accounts were updated
        updated_accounts = set()
        
        # Update each account's balance based on transaction entries
        for entry in transaction.entries:
            account_index = None
            for i, acc in enumerate(accounts):
                if acc['id'] == entry.accountId:
                    account_index = i
                    break
                    
            if account_index is None:
                return False, f"Account {entry.accountId} not found"
                
            account = accounts[account_index]
            
            # Validate if account is active
            if not account.get('active', True):
                return False, f"Account {entry.accountId} is inactive"
                
            # Get normal balance type
            normal_balance = account.get('normalBalanceType', 'debit')
            current_balance = float(account.get('currentBalance', 0))
            
            # Calculate balance change based on normal balance type
            if normal_balance == 'debit':
                # For debit-normal accounts:
                # Debit increases the balance, Credit decreases it
                if entry.type == 'debit':
                    account['currentBalance'] = current_balance + entry.amount
                else:  # credit
                    account['currentBalance'] = current_balance - entry.amount
            else:  # credit normal
                # For credit-normal accounts:
                # Credit increases the balance, Debit decreases it
                if entry.type == 'credit':
                    account['currentBalance'] = current_balance + entry.amount
                else:  # debit
                    account['currentBalance'] = current_balance - entry.amount
                
            # Update last transaction date
            account['lastTransactionDate'] = transaction.date
            
            # Mark account as updated
            updated_accounts.add(account['id'])
            
        # Calculate totals by summing all account balances
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
        
        # Save changes
        with open(file_path, 'w') as f:
            json.dump(chart_data, f, indent=2)
            
        return True, None
        
    except Exception as e:
        return False, str(e)

def reverse_account_balances(transaction: Transaction) -> tuple[bool, Optional[str]]:
    """Reverse account balances in the chart of accounts when voiding a transaction"""
    try:
        uid = get_user_id()
        if not uid:
            return False, "User ID not found"
        
        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return False, "Chart of accounts not found"
        
        # Load chart of accounts
        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts = chart_data.get('accounts', [])
            
        # Track which accounts were updated
        updated_accounts = set()
        
        # Reverse each account's balance based on transaction entries
        for entry in transaction.entries:
            account_index = None
            for i, acc in enumerate(accounts):
                if acc['id'] == entry.accountId:
                    account_index = i
                    break
                    
            if account_index is None:
                return False, f"Account {entry.accountId} not found"
                
            account = accounts[account_index]
            
            # Validate if account is active
            if not account.get('active', True):
                return False, f"Account {entry.accountId} is inactive"
                
            # Get normal balance type
            normal_balance = account.get('normalBalanceType', 'debit')
            
            # Calculate balance change (reverse of original)
            if normal_balance == 'debit':
                # For debit-normal accounts:
                # Debit increases the balance, Credit decreases it
                if entry.type == 'debit':
                    account['currentBalance'] = account.get('currentBalance', 0) - entry.amount
                else:  # credit
                    account['currentBalance'] = account.get('currentBalance', 0) + entry.amount
            else:  # credit normal
                # For credit-normal accounts:
                # Credit increases the balance, Debit decreases it
                if entry.type == 'credit':
                    account['currentBalance'] = account.get('currentBalance', 0) - entry.amount
                else:  # debit
                    account['currentBalance'] = account.get('currentBalance', 0) + entry.amount
                
            # Mark account as updated
            updated_accounts.add(account['id'])
            
        # Save changes
        with open(file_path, 'w') as f:
            json.dump(chart_data, f, indent=2)
            
        return True, None
        
    except Exception as e:
        return False, str(e)

@transactions_bp.route('/validate', methods=['POST'])
def validate_transaction():
    """Validate a transaction before creation"""
    try:
        data = request.get_json()
        
        # Basic validation
        if not data:
            return jsonify({'is_valid': False, 'error': 'No data provided'}), 400
            
        if 'entries' not in data or not data['entries']:
            return jsonify({'is_valid': False, 'error': 'No entries provided'}), 400
            
        # Validate transaction type and sub-type
        transaction_type = data.get('transaction_type')
        sub_type = data.get('sub_type')
        
        if not transaction_type:
            return jsonify({'is_valid': False, 'error': 'Transaction type is required'}), 400
            
        # Validate accounts
        is_valid, error_message = validate_transaction_accounts(
            transaction_type,
            sub_type,
            data['entries']
        )
        
        if not is_valid:
            return jsonify({'is_valid': False, 'error': error_message}), 400
            
        # Validate debits and credits balance
        total_debits = sum(float(entry['amount']) for entry in data['entries'] if entry['type'] == 'debit')
        total_credits = sum(float(entry['amount']) for entry in data['entries'] if entry['type'] == 'credit')
        
        if abs(total_debits - total_credits) > 0.01:  # Allow for small floating-point differences
            return jsonify({'is_valid': False, 'error': 'Debits and credits must balance'}), 400
            
        return jsonify({'is_valid': True}), 200
        
    except Exception as e:
        return jsonify({'is_valid': False, 'error': str(e)}), 500

@transactions_bp.route('/create', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.get_json()
        
        # Validate the transaction first
        validation_response = validate_transaction()
        if validation_response[1] != 200:
            return validation_response
            
        # Load chart of accounts to get account names
        uid = get_user_id()
        if not uid:
            return jsonify({'success': False, 'error': 'User ID not found'}), 400
        
        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Chart of accounts not found'}), 400
        
        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts = {acc['id']: acc for acc in chart_data.get('accounts', [])}
        
        # Add account names to entries
        for entry in data['entries']:
            account = accounts.get(entry['accountId'])
            if account:
                entry['accountName'] = account['name']
            
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Create transaction object
        transaction = Transaction.from_dict({
            'id': transaction_id,
            **data
        })
        
        # Load existing transactions
        transactions_data = load_transactions()
        
        # Add new transaction
        transactions_data['transactions'].append(transaction.to_dict())
        
        # Save updated transactions
        if save_transactions(transactions_data):
            return jsonify({
                'success': True,
                'message': 'Transaction created successfully',
                'transaction': transaction.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save transaction'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@transactions_bp.route('/list_transactions', methods=['GET'])
def list_transactions():
    """Get a paginated list of transactions with optional filters"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = Transaction.load_user_transactions(uid)
        transactions = data.get('transactions', [])

        # Apply filters
        status = request.args.get('status')
        if status:
            transactions = [t for t in transactions if t['status'] == status]

        transaction_type = request.args.get('type')
        if transaction_type:
            transactions = [t for t in transactions if t['transaction_type'] == transaction_type]

        reference_type = request.args.get('reference_type')
        if reference_type:
            transactions = [t for t in transactions if t['reference_type'] == reference_type]

        reference_id = request.args.get('reference_id')
        if reference_id:
            transactions = [t for t in transactions if t['reference_id'] == reference_id]

        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)

        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        start = (page - 1) * per_page
        end = start + per_page

        paginated_transactions = transactions[start:end]
        total_pages = (len(transactions) + per_page - 1) // per_page

        return jsonify({
            'transactions': paginated_transactions,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': len(transactions)
        })

    except Exception as e:
        print(f"Error listing transactions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@transactions_bp.route('/get_transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get details of a specific transaction"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = Transaction.load_user_transactions(uid)
        transaction = next(
            (t for t in data.get('transactions', []) if t['id'] == transaction_id), 
            None
        )
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
            
        return jsonify(transaction)
        
    except Exception as e:
        print(f"Error getting transaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@transactions_bp.route('/patch/<transaction_id>', methods=['PATCH'])
def patch_transaction(transaction_id):
    """Update specific fields of a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                if t['status'] != 'draft':
                    return jsonify({
                        'message': 'Only draft transactions can be updated'
                    }), 400
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Update fields
        patch_data = request.get_json()
        current_transaction = transactions[transaction_index]
        current_transaction.update({
            k: v for k, v in patch_data.items()
            if k in ['date', 'description', 'reference', 'entries']
        })
        current_transaction['updated_at'] = datetime.utcnow().date().isoformat()
        
        # Validate updated transaction
        transaction = Transaction.from_dict(current_transaction)
        is_valid, error = transaction.validate()
        if not is_valid:
            return jsonify({'message': error}), 400
            
        # Save changes
        transactions[transaction_index] = transaction.to_dict()
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error updating transaction: {str(e)}'}), 500

@transactions_bp.route('/delete/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        transaction_to_delete = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                transaction_index = i
                transaction_to_delete = t
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # If transaction was posted, reverse its effect on account balances
        if transaction_to_delete.get('status') == 'posted':
            transaction_obj = Transaction(**transaction_to_delete)
            success, error = reverse_account_balances(transaction_obj)
            if not success:
                return jsonify({'message': f'Failed to reverse balances: {error}'}), 500
            
        # Remove transaction
        transactions.pop(transaction_index)
        
        # Save changes
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        # Recalculate all account balances from scratch
        uid = get_user_id()
        if not uid:
            return jsonify({'message': 'User ID not found'}), 401
            
        file_path = os.path.join(DATA_DIR, uid, 'chart_of_accounts.json')
        if not os.path.exists(file_path):
            return jsonify({'message': 'Chart of accounts not found'}), 404
            
        # Load chart of accounts
        with open(file_path, 'r') as f:
            chart_data = json.load(f)
            accounts = chart_data.get('accounts', [])
            
        # Reset all balances to opening balance
        for account in accounts:
            account['currentBalance'] = account.get('openingBalance', 0.0)
            account['lastTransactionDate'] = None
            
        # Reapply all posted transactions
        for transaction in transactions:
            if transaction.get('status') == 'posted':
                transaction_obj = Transaction(**transaction)
                success, error = update_account_balances(transaction_obj)
                if not error:
                    return jsonify({'message': f'Failed to update balances: {error}'}), 500
            
        return jsonify({'message': 'Transaction deleted successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Error deleting transaction: {str(e)}'}), 500

@transactions_bp.route('/post/<transaction_id>', methods=['POST'])
def post_transaction(transaction_id):
    """Post a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Get transaction object
        transaction = Transaction.from_dict(transactions[transaction_index])
        
        # Check if transaction is already posted
        if transaction.status == 'posted':
            return jsonify({'message': 'Transaction is already posted'}), 400
            
        # Validate transaction
        is_valid, error = transaction.validate()
        if not is_valid:
            return jsonify({'message': error}), 400
            
        # Update account balances
        success, error = update_account_balances(transaction)
        if not success:
            return jsonify({'message': f'Failed to update account balances: {error}'}), 500
            
        # Update transaction status
        now = datetime.utcnow().date().isoformat()
        transaction.status = 'posted'
        transaction.posted_at = now
        transaction.updated_at = now
        
        # Save changes to transaction
        transactions[transaction_index] = transaction.to_dict()
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save transaction changes'}), 500
            
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error posting transaction: {str(e)}'}), 500

@transactions_bp.route('/void/<string:transaction_id>', methods=['POST'])
def void_transaction(transaction_id):
    """Void a transaction"""
    try:
        # Load transactions
        transactions_data = load_transactions()
        transactions = transactions_data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        for i, txn in enumerate(transactions):
            if txn['id'] == transaction_id:
                transaction_index = i
                break
                
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        transaction = transactions[transaction_index]
        
        # Check if transaction can be voided
        if transaction['status'] != 'posted':
            return jsonify({'message': 'Only posted transactions can be voided'}), 400
            
        if transaction.get('voided_at'):
            return jsonify({'message': 'Transaction is already voided'}), 400
            
        # Create Transaction object to reverse balances
        transaction_obj = Transaction.from_dict(transaction)
        success, error = reverse_account_balances(transaction_obj)
        if not success:
            return jsonify({'message': f'Failed to reverse account balances: {error}'}), 500
            
        # Update transaction status
        transaction['status'] = 'void'
        transaction['voided_at'] = datetime.utcnow().isoformat()
        transaction['voided_by'] = None  # TODO: Add user info
        
        # Save changes
        transactions_data['transactions'] = transactions
        if not save_transactions(transactions_data):
            return jsonify({'message': 'Failed to save voided transaction'}), 500
            
        # If this is an invoice payment, update the invoice status
        if transaction['reference_type'] == 'invoice_payment':
            invoice_id = transaction['reference_id'].split('_')[0]  # Get invoice ID from reference
            
            # Load invoices
            try:
                uid = get_user_id()
                if not uid:
                    return jsonify({'message': 'User ID not found'}), 400
                
                with open(os.path.join(DATA_DIR, uid, 'invoices.json'), 'r') as f:
                    invoices_data = json.load(f)
            except:
                invoices_data = {}
                
            # Find invoice
            invoice = next((inv for inv in invoices_data.get('invoices', []) if inv['id'] == invoice_id), None)
            if invoice:
                # Recalculate total paid
                total_paid = sum(
                    float(p.get('amount', 0)) 
                    for p in invoice.get('payments', [])
                    if p.get('transaction_id') != transaction_id  # Exclude voided payment
                )
                
                # Update balance and status
                invoice['balance_due'] = float(invoice['total_amount']) - total_paid
                
                if total_paid == 0:
                    invoice['status'] = 'posted'
                elif total_paid < float(invoice['total_amount']):
                    invoice['status'] = 'partially_paid'
                else:
                    invoice['status'] = 'paid'
                    
                # Save changes
                with open(os.path.join(DATA_DIR, uid, 'invoices.json'), 'w') as f:
                    json.dump(invoices_data, f, indent=2)
            
        return jsonify({
            'message': 'Transaction voided successfully',
            'transaction': transaction
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error voiding transaction: {str(e)}'}), 500
