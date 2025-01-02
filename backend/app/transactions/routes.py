from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import random

from . import transactions_bp
from .models import Transaction, TransactionEntry, TransactionType

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')
CHART_OF_ACCOUNTS_FILE = os.path.join(DATA_DIR, 'chart_of_accounts.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_default_accounts() -> Dict[str, str]:
    """Get default account IDs from chart of accounts"""
    try:
        with open(CHART_OF_ACCOUNTS_FILE, 'r') as f:
            chart_data = json.load(f)
            accounts = chart_data.get('accounts', [])
            
            # Find Accounts Receivable account
            accounts_receivable = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Accounts Receivable' 
                and acc['isDefault'] 
                and acc['active']),
                None
            )
            
            # Find Sales Revenue account
            sales_revenue = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Income'
                and acc['name'] == 'Sales Revenue'
                and acc['isDefault'] 
                and acc['active']),
                None
            )
            
            # Find COGS account
            cogs = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Cost of Goods Sold'
                and acc['isDefault'] 
                and acc['active']),
                None
            )
            
            # Find Inventory Asset account
            inventory_asset = next(
                (acc['id'] for acc in accounts 
                if acc['accountType'] == 'Other Current Asset'
                and acc['detailType'] == 'Inventory'
                and acc['isDefault'] 
                and acc['active']),
                None
            )
            
            if not accounts_receivable or not sales_revenue or not cogs or not inventory_asset:
                raise Exception("Required default accounts not found in chart of accounts")
                
            return {
                'accounts_receivable': accounts_receivable,
                'sales_revenue': sales_revenue,
                'cogs': cogs,
                'inventory_asset': inventory_asset
            }
    except Exception as e:
        print(f"Error loading default accounts: {str(e)}")
        return {
            'accounts_receivable': '1100-0001',  # Fallback Accounts Receivable
            'sales_revenue': '4000-0001',        # Fallback Sales Revenue
            'cogs': '5000-0001',                 # Fallback COGS
            'inventory_asset': '1200-0001'       # Fallback Inventory Asset
        }

# Get default accounts
DEFAULT_ACCOUNTS = get_default_accounts()

def generate_transaction_id() -> str:
    """Generate a random transaction ID"""
    return f"TXN-{random.randint(10000, 99999)}"

def load_transactions() -> Dict:
    """Load transactions data from JSON file"""
    try:
        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading transactions data: {str(e)}")
    return {'transactions': []}

def save_transactions(data: Dict) -> bool:
    """Save transactions data to JSON file"""
    try:
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving transactions data: {str(e)}")
        return False

def create_transaction_direct(transaction_data: dict):
    """Create a new transaction directly from code (not via HTTP)"""
    try:
        # Load chart of accounts to get account names
        with open(CHART_OF_ACCOUNTS_FILE, 'r') as f:
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
                with open(os.path.join(DATA_DIR, 'products.json'), 'r') as f:
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
                    'accountId': DEFAULT_ACCOUNTS['accounts_receivable'],
                    'amount': amount,
                    'type': 'debit',
                    'description': f"{description} - Revenue ({accounts_map.get(DEFAULT_ACCOUNTS['accounts_receivable'], 'Accounts Receivable')})"
                },
                {
                    'accountId': DEFAULT_ACCOUNTS['sales_revenue'],
                    'amount': amount,
                    'type': 'credit',
                    'description': f"{description} - Revenue ({accounts_map.get(DEFAULT_ACCOUNTS['sales_revenue'], 'Sales Revenue')})"
                }
            ])
            
            # Add COGS entries for inventory items
            if product_type == 'inventory_item' and cost_amount > 0:
                entries.extend([
                    {
                        'accountId': DEFAULT_ACCOUNTS['cogs'],
                        'amount': cost_amount,
                        'type': 'debit',
                        'description': f"{description} - Cost of Goods Sold ({accounts_map.get(DEFAULT_ACCOUNTS['cogs'], 'Cost of Goods Sold')})"
                    },
                    {
                        'accountId': DEFAULT_ACCOUNTS['inventory_asset'],
                        'amount': cost_amount,
                        'type': 'credit',
                        'description': f"{description} - Inventory Reduction ({accounts_map.get(DEFAULT_ACCOUNTS['inventory_asset'], 'Inventory Asset')})"
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
        with open(CHART_OF_ACCOUNTS_FILE, 'r') as f:
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
    valid_types = {
        'sale': ['Accounts Receivable', 'Income', 'Bank', 'Other Current Asset'],
        'purchase': ['Accounts Payable', 'Other Current Asset', 'Expense', 'Bank'],
        'payment_received': ['Bank', 'Accounts Receivable'],
        'payment_made': ['Bank', 'Accounts Payable'],
        'expense': ['Expense', 'Bank', 'Credit Card'],
        'transfer': ['Bank', 'Other Current Asset'],
        'adjustment': ['Other Current Asset', 'Income', 'Expense']
    }
    return valid_types.get(transaction_type, [])

def update_account_balances(transaction: Transaction) -> tuple[bool, Optional[str]]:
    """Update account balances in the chart of accounts when posting a transaction"""
    try:
        # Load chart of accounts
        with open(CHART_OF_ACCOUNTS_FILE, 'r') as f:
            chart_data = json.load(f)
            accounts = chart_data.get('accounts', [])
            
        # Track which accounts were updated
        updated_accounts = set()
        total_assets = 0
        total_liabilities = 0
        total_equity = 0
        total_income = 0
        total_expense = 0
        
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
            
            # Update totals based on account type
            account_type = account.get('accountType', '')
            balance = float(account.get('currentBalance', 0))
            
            if account_type in ['Bank', 'Other Current Asset', 'Fixed Asset']:
                total_assets += balance
            elif account_type in ['Credit Card', 'Accounts Payable', 'Other Current Liability', 'Long Term Liability']:
                total_liabilities += balance
            elif account_type == 'Equity':
                total_equity += balance
            elif account_type == 'Income':
                total_income += balance
            elif account_type in ['Cost of Goods Sold', 'Expense']:
                total_expense += balance
        
        # Update summary
        chart_data['summary'] = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_income': total_income,
            'total_expense': total_expense,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Save changes
        with open(CHART_OF_ACCOUNTS_FILE, 'w') as f:
            json.dump(chart_data, f, indent=2)
            
        return True, None
        
    except Exception as e:
        return False, str(e)

def reverse_account_balances(transaction: Transaction) -> tuple[bool, Optional[str]]:
    """Reverse account balances in the chart of accounts when voiding a transaction"""
    try:
        # Load chart of accounts
        with open(CHART_OF_ACCOUNTS_FILE, 'r') as f:
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
        with open(CHART_OF_ACCOUNTS_FILE, 'w') as f:
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
        with open(CHART_OF_ACCOUNTS_FILE, 'r') as f:
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

@transactions_bp.route('/list', methods=['GET'])
def list_transactions():
    """Get a paginated list of transactions with optional filters"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        transaction_type = request.args.get('type')
        sub_type = request.args.get('sub_type')
        status = request.args.get('status')
        reference_type = request.args.get('reference_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Load transactions
        transactions_data = load_transactions()
        transactions = transactions_data.get('transactions', [])
        
        # Load invoices to get payment information
        try:
            with open(os.path.join(DATA_DIR, 'invoices.json'), 'r') as f:
                invoices_data = json.load(f)
                invoices = {inv['id']: inv for inv in invoices_data.get('invoices', [])}
        except:
            invoices = {}
        
        # Apply filters
        if transaction_type:
            transactions = [t for t in transactions if t.get('transaction_type') == transaction_type]
        if sub_type:
            transactions = [t for t in transactions if t.get('sub_type') == sub_type]
        if status:
            transactions = [t for t in transactions if t.get('status') == status]
        if reference_type:
            transactions = [t for t in transactions if t.get('reference_type') == reference_type]
        if start_date:
            transactions = [t for t in transactions if t.get('date', '') >= start_date]
        if end_date:
            transactions = [t for t in transactions if t.get('date', '') <= end_date]
            
        # Add payment information for invoice transactions
        for transaction in transactions:
            if transaction.get('reference_type') == 'invoice':
                invoice_id = transaction.get('reference_id')
                if invoice_id and invoice_id in invoices:
                    invoice = invoices[invoice_id]
                    transaction['invoice_status'] = invoice.get('status', 'unknown')
                    transaction['invoice_total'] = invoice.get('total_amount', 0)
                    transaction['invoice_balance'] = invoice.get('balance_due', 0)
                    transaction['invoice_paid'] = float(invoice.get('total_amount', 0)) - float(invoice.get('balance_due', 0))
                    transaction['last_payment_date'] = invoice.get('last_payment_date')
            elif transaction.get('reference_type') == 'invoice_payment':
                # For payment transactions, extract the invoice ID from reference_id (format: "invoice_id_payment_id")
                if transaction.get('reference_id'):
                    invoice_id = transaction.get('reference_id').split('_')[0]
                    if invoice_id in invoices:
                        invoice = invoices[invoice_id]
                        transaction['invoice_status'] = invoice.get('status', 'unknown')
                        transaction['invoice_total'] = invoice.get('total_amount', 0)
                        transaction['invoice_balance'] = invoice.get('balance_due', 0)
                        transaction['invoice_paid'] = float(invoice.get('total_amount', 0)) - float(invoice.get('balance_due', 0))
                        transaction['last_payment_date'] = invoice.get('last_payment_date')
        
        # Sort transactions by date (newest first)
        transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Calculate pagination
        total_items = len(transactions)
        total_pages = (total_items + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Get paginated transactions
        paginated_transactions = transactions[start_idx:end_idx]
        
        return jsonify({
            'transactions': paginated_transactions,
            'pagination': {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error listing transactions: {str(e)}'}), 500

@transactions_bp.route('/get/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get details of a specific transaction"""
    try:
        # Load transactions
        data = load_transactions()
        
        # Find transaction
        transaction = next(
            (t for t in data.get('transactions', []) if t['id'] == transaction_id),
            None
        )
        
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404
            
        return jsonify(transaction)
        
    except Exception as e:
        return jsonify({'message': f'Error getting transaction: {str(e)}'}), 500

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
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Remove transaction
        transactions.pop(transaction_index)
        
        # Save changes
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
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
            with open(os.path.join(DATA_DIR, 'invoices.json'), 'r') as f:
                invoices_data = json.load(f)
                
            # Find invoice
            invoice = next((inv for inv in invoices_data['invoices'] if inv['id'] == invoice_id), None)
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
                with open(os.path.join(DATA_DIR, 'invoices.json'), 'w') as f:
                    json.dump(invoices_data, f, indent=2)
            
        return jsonify({
            'message': 'Transaction voided successfully',
            'transaction': transaction
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error voiding transaction: {str(e)}'}), 500
