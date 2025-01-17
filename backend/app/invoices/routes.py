from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from firebase_admin import auth

from . import invoices_bp
from .models import Invoice, InvoicesSummary, Payment, INVOICE_STATUSES, PAYMENT_METHODS, PAYMENT_TERMS
from app.transactions.models import Transaction, TransactionType, TransactionSubType, TransactionEntry
from app.chart_of_accounts.models import Account
from app.transactions.routes import create_transaction_direct, load_transactions, save_transactions, post_transaction, generate_transaction_id
from app.chart_of_accounts.routes import load_chart_of_accounts
from app.products.routes import load_products
from app.base.base_models import LineItem

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

# Get account IDs from chart of accounts
def get_system_accounts(uid: str = None):
    """Get system accounts, optionally for a specific user"""
    try:
        accounts = load_chart_of_accounts(uid).get('accounts', []) if uid else []

        ar_account = next((acc for acc in accounts if acc['accountType'] == 'Accounts Receivable' and acc['isDefault']), None)
        ap_account = next((acc for acc in accounts if acc['accountType'] == 'Accounts Payable' and acc['isDefault']), None)
        sales_account = next((acc for acc in accounts if acc['accountType'] == 'Income' and acc['isDefault']), None)
        cogs_account = next((acc for acc in accounts if acc['accountType'] == 'Cost of Goods Sold' and acc['isDefault']), None)
        inventory_account = next((acc for acc in accounts if acc['accountType'] == 'Other Current Asset' and acc['detailType'] == 'Inventory' and acc['isDefault']), None)
        cash_account = next((acc for acc in accounts if acc['accountType'] == 'Bank' and acc['isDefault']), None)
        
        if not all([ar_account, ap_account, sales_account, cogs_account, inventory_account, cash_account]):
            raise Exception("Required system accounts not found in chart of accounts")
            
        return {
            'ACCOUNTS_RECEIVABLE_ID': ar_account,
            'ACCOUNTS_PAYABLE_ID': ap_account,
            'SALES_REVENUE_ID': sales_account,
            'COGS_ID': cogs_account,
            'INVENTORY_ASSET_ID': inventory_account,
            'CASH_AND_BANK_ID': cash_account
        }
    except Exception as e:
        # Fallback values in case of error - these should match your chart of accounts
        return {
            'ar_account': {'id': "1100-0001", 'name': "Accounts Receivable", 'accountType': "Accounts Receivable"},
            'ap_account': {'id': "2100-0001", 'name': "Accounts Payable", 'accountType': "Accounts Payable"},
            'sales_account': {'id': "4000-0001", 'name': "Sales Revenue", 'accountType': "Income"},
            'cogs_account': {'id': "5000-0001", 'name': "Cost of Goods Sold", 'accountType': "Cost of Goods Sold"},
            'inventory_account': {'id': "1200-0001", 'name': "Inventory Asset", 'accountType': "Other Current Asset"},
            'cash_account': {'id': "1000-0001", 'name': "Cash and Bank", 'accountType': "Bank"}
        }

# Initialize system accounts with fallback values
system_accounts = get_system_accounts()  # Don't pass uid during module initialization
ACCOUNTS_RECEIVABLE_ID = system_accounts['ar_account']
ACCOUNTS_PAYABLE_ID = system_accounts['ap_account']
SALES_REVENUE_ID = system_accounts['sales_account']
COGS_ID = system_accounts['cogs_account']
INVENTORY_ASSET_ID = system_accounts['inventory_account']
CASH_AND_BANK_ID = system_accounts['cash_account']

def get_current_system_accounts():
    """Get current system accounts for the authenticated user"""
    uid = get_user_id()
    if uid:
        return get_system_accounts(uid)
    return system_accounts

def deep_update(original: Dict, update: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def load_invoices(uid: str = None) -> Dict:
    """Load invoices data from JSON file"""
    try:
        if not uid:
            return {'invoices': [], 'summary': {}}
            
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', uid, 'invoices.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading invoices data: {str(e)}")
    return {'invoices': [], 'summary': {}}

def save_invoices(uid: str, data: Dict) -> None:
    """Save invoices data to JSON file"""
    try:
        # Update summary before saving
        summary = update_summary(data['invoices'])
        data['summary'] = summary.to_dict()
        data['metadata'] = {
            'lastUpdated': datetime.utcnow().isoformat(),
            'createdAt': data.get('metadata', {}).get('createdAt', datetime.utcnow().isoformat())
        }
        
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', uid, 'invoices.json')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving invoices data: {str(e)}")

def update_summary(invoices: List[Dict]) -> InvoicesSummary:
    """Update invoices summary information"""
    summary = InvoicesSummary()
    current_time = datetime.now()
    
    for invoice in invoices:
        # Skip cancelled invoices in amount calculations
        if invoice['status'] == 'cancelled':
            summary.cancelled_count += 1
            continue
            
        # Get payment info
        total_paid = sum(payment['amount'] for payment in invoice.get('payments', []))
        balance_due = invoice['total'] - total_paid
        
        # Update counts and amounts based on status
        if invoice['status'] == 'draft':
            summary.draft_count += 1
            summary.draft_amount += balance_due
        elif invoice['status'] == 'sent':  # Changed from 'sent'
            summary.sent_count += 1
            summary.sent_amount += balance_due
            # Check for overdue
            if 'due_date' in invoice:
                due_date = datetime.fromisoformat(invoice['due_date'])
                if due_date < current_time:
                    summary.overdue_count += 1
                    summary.overdue_amount += balance_due
        elif invoice['status'] == 'paid':
            summary.paid_count += 1
            summary.paid_amount += invoice['total']
        elif invoice['status'] == 'void':
            summary.void_count += 1
            summary.void_amount += balance_due
            
        # Update payment tracking
        if invoice['status'] not in ['paid', 'cancelled', 'void']:
            summary.total_receivable += balance_due
        summary.total_collected += total_paid
    
    return summary

def get_next_invoice_number() -> str:
    """Generate the next invoice number"""
    data = load_invoices()
    invoices = data.get('invoices', [])
    if not invoices:
        return "INV-2024-001"
    
    current_year = datetime.now().year
    year_invoices = [inv for inv in invoices if inv['invoice_no'].startswith(f"INV-{current_year}")]
    
    if not year_invoices:
        return f"INV-{current_year}-001"
    
    last_number = max(int(inv['invoice_no'].split('-')[2]) for inv in year_invoices)
    return f"INV-{current_year}-{(last_number + 1):03d}"

def generate_invoice_id() -> str:
    """Generate a random 8-digit ID with a dash in the middle"""
    # Generate two 4-digit numbers
    first_half = str(random.randint(1000, 9999))
    second_half = str(random.randint(1000, 9999))
    return f"{first_half}-{second_half}"

def is_id_unique(id: str, invoices: List[Dict]) -> bool:
    """Check if an ID is unique among existing invoices"""
    return not any(inv.get('id') == id for inv in invoices)

def generate_payment_id():
    """Generate a random 8-digit ID with a dash in the middle for payments"""
    while True:
        # Generate two 4-digit numbers
        first = str(random.randint(1000, 9999))
        second = str(random.randint(1000, 9999))
        payment_id = f"{first}-{second}"
        return payment_id  # No need to check uniqueness for payments

def check_and_update_status(invoice: Dict) -> None:
    """Update invoice status based on payments and due date"""
    now = datetime.utcnow()
    due_date = datetime.fromisoformat(invoice['due_date'])
    total_paid = sum(payment['amount'] for payment in invoice.get('payments', []))
    
    # Update balance due
    invoice['balance_due'] = invoice['total'] - total_paid
    
    if total_paid >= invoice['total']:
        invoice['status'] = 'paid'
    elif total_paid > 0:
        invoice['status'] = 'partially_paid'
        if due_date < now:
            invoice['status'] = 'overdue'
    elif due_date < now:
        invoice['status'] = 'overdue'

def calculate_due_date(invoice_date: str, payment_terms: str) -> str:
    """Calculate due date based on invoice date and payment terms"""
    try:
        # Convert invoice_date string to datetime
        date = datetime.strptime(invoice_date, '%Y-%m-%d')
        
        # Calculate due date based on payment terms
        if payment_terms == 'net_15':
            date = date + timedelta(days=15)
        elif payment_terms == 'net_30':
            date = date + timedelta(days=30)
        elif payment_terms == 'net_60':
            date = date + timedelta(days=60)
        
        # Return date in YYYY-MM-DD format
        return date.strftime('%Y-%m-%d')
    except Exception:
        # If any error occurs, return the invoice date
        return invoice_date

def validate_account_id(account_id: str, account_type: str) -> str:
    """Validate account ID exists and is of correct type. Returns default if invalid."""
    try:
        accounts = load_chart_of_accounts().get('accounts', [])
        account = next((acc for acc in accounts if acc['id'] == account_id), None)
        
        if account:
            if account_type == 'income' and account['accountType'] in ['Income', 'Revenue']:
                return account_id
            elif account_type == 'receivable' and account['accountType'] == 'Accounts Receivable':
                return account_id
            elif account_type == 'payable' and account['accountType'] == 'Accounts Payable':
                return account_id
            elif account_type == 'asset' and account['accountType'] in ['Asset', 'Cash', 'Bank']:
                return account_id
                
        # Return default based on type
        if account_type == 'income':
            return SALES_REVENUE_ID
        elif account_type == 'receivable':
            return ACCOUNTS_RECEIVABLE_ID
        elif account_type == 'payable':
            return ACCOUNTS_PAYABLE_ID
        elif account_type == 'asset':
            return CASH_AND_BANK_ID
            
    except Exception as e:
        print(f"Error validating account ID: {str(e)}")
        return SALES_REVENUE_ID if account_type == 'income' else ACCOUNTS_RECEIVABLE_ID

def create_invoice_transaction(invoice: Invoice, uid: str, sub_type: str = 'invoice_draft') -> None:
    """Create a transaction record for an invoice"""
    try:
        # Get invoice data
        accounts = get_system_accounts(uid)
        if not accounts:
            raise ValueError("System accounts not found")

        # Calculate total amount
        total_amount = invoice.total

        # Create entries list
        entries = []
        
        # Add revenue entries
        entries.extend([
            TransactionEntry(
                accountId=accounts['ACCOUNTS_RECEIVABLE_ID']['id'],
                accountName=accounts['ACCOUNTS_RECEIVABLE_ID']['name'],
                amount=total_amount,
                type='debit',
                description=f"Invoice {invoice.invoice_no} - Accounts Receivable"
            ),
            TransactionEntry(
                accountId=accounts['SALES_REVENUE_ID']['id'],
                accountName=accounts['SALES_REVENUE_ID']['name'],
                amount=total_amount,
                type='credit',
                description=f"Invoice {invoice.invoice_no} - Sales Revenue"
            )
        ])
        
        # Add COGS entries only for inventory items
        total_cost = 0
        try:
            products = load_products().get('products', []) 

            for item in invoice.line_items:
                product = next((p for p in products if p['id'] == item.product_id), None)
                if product and product.get('type') == 'inventory_item':
                    cost_amount = float(product.get('cost_price', 0)) * item.quantity
                    total_cost += cost_amount
        except Exception as e:
            print(f"Error calculating COGS: {str(e)}")
        
        if total_cost > 0:
            entries.extend([
                TransactionEntry(
                    accountId=accounts['COGS_ID']['id'],
                    accountName=accounts['COGS_ID']['name'],
                    amount=total_cost,
                    type='debit',
                    description=f"Invoice {invoice.invoice_no} - COGS"
                ),
                TransactionEntry(
                    accountId=accounts['INVENTORY_ASSET_ID']['id'],
                    accountName=accounts['INVENTORY_ASSET_ID']['name'],
                    amount=total_cost,
                    type='credit',
                    description=f"Invoice {invoice.invoice_no} - Inventory"
                )
            ])
        
        # Create transaction
        transaction = Transaction(
            id=generate_transaction_id(),
            date=invoice.invoice_date,
            description=f"Invoice {invoice.invoice_no}",
            transaction_type=TransactionType.INVOICE.value,
            sub_type=sub_type,
            reference_type='invoice',
            reference_id=invoice.id,
            status='draft' if invoice.status == 'draft' else 'posted',
            customer_name=invoice.customer_name,
            amount=total_amount,
            entries=entries,
            invoice_total=total_amount,
            invoice_paid=total_amount - invoice.balance_due,
            invoice_balance=invoice.balance_due,
            invoice_status=invoice.status,
            last_payment_date=invoice.last_payment_date
        ).to_dict()

        return transaction
        
        # transactions_data = Transaction.load_user_transactions(uid)
        # transactions_data['transactions'].append(transaction.to_dict())
        # Transaction.save_user_transactions(uid, transactions_data)

        # if invoice.status in ['sent', 'paid']:
        #     post_transaction(transaction.id, uid)

    except Exception as e:
        print(f"Error in create_transaction_direct: {str(e)}")
        raise

def update_invoice_transaction(invoice_data: Dict, sub_type: str) -> None:
    """Update the transaction record for an invoice"""
    try:
        uid = get_user_id()
        if not uid:
            raise ValueError("User ID not found")
        
        invoice = Invoice.from_dict(invoice_data)

        new_transaction = create_invoice_transaction(invoice, uid, sub_type)
        if not new_transaction:
            return

        transactions_data = Transaction.load_user_transactions(uid)
        transactions = transactions_data.get('transactions', [])

        idx = next((i for i, t in enumerate(transactions) 
                   if t.get('reference_type') == 'invoice' 
                   and t.get('reference_id') == invoice_data['id']), None)

        if idx is not None:
            transactions[idx] = new_transaction
        else:
            transactions.append(new_transaction)

        Transaction.save_user_transactions(uid, {'transactions': transactions})

    except Exception as e:
        print(f"Error updating invoice transaction: {str(e)}")
        raise

def delete_invoice_transaction(invoice_id: str, uid: str) -> None:
    """Delete the transaction record for an invoice and its payments"""
    try:
        # Load transactions
        transactions_data = Transaction.load_user_transactions(uid)
        transactions = transactions_data.get('transactions', [])

        # Remove both invoice and payment transactions
        filtered_transactions = [
            t for t in transactions 
            if not (
                (t.get('reference_type') == 'invoice' and t.get('reference_id') == invoice_id) or
                (t.get('transaction_type') == TransactionType.PAYMENT_RECEIVED.value and 
                 t.get('reference_id', '').startswith(f"{invoice_id}_"))
            )
        ]

        # Save updated transactions
        Transaction.save_user_transactions(uid, {'transactions': filtered_transactions})

    except Exception as e:
        print(f"Error deleting invoice transaction: {str(e)}")
        raise

def create_payment_transaction(invoice: Invoice, payment: Payment, uid: str) -> None:
    """Create a transaction record for a payment"""
    try:
        # Get system accounts
        accounts = get_system_accounts(uid)
        if not accounts:
            raise ValueError("System accounts not found")

        # Create entries list
        entries = [
            TransactionEntry(
                accountId=accounts['cash_account']['id'],
                accountName=accounts['cash_account']['name'],
                amount=payment.amount,
                type='debit',
                description=f"Payment for Invoice {invoice.invoice_no}"
            ),
            TransactionEntry(
                accountId=accounts['ar_account']['id'],
                accountName=accounts['ar_account']['name'],
                amount=payment.amount,
                type='credit',
                description=f"Payment for Invoice {invoice.invoice_no} - AR"
            )
        ]

        # Create transaction
        transaction = Transaction(
            id=generate_transaction_id(),
            date=payment.date,
            description=f"Payment for Invoice {invoice.invoice_no}",
            transaction_type=TransactionType.PAYMENT_RECEIVED.value,
            sub_type='customer_payment',
            reference_type='payment',
            reference_id=f"{invoice.id}_{payment.id}",
            status='posted',
            customer_name=invoice.customer_name,
            amount=payment.amount,
            entries=entries,
            payment_method=payment.payment_method,
            payment_reference=payment.reference_number
        )

        # Save transaction
        transactions_data = Transaction.load_user_transactions(uid)
        transactions_data['transactions'].append(transaction.to_dict())
        Transaction.save_user_transactions(uid, transactions_data)

        # Update payment with transaction ID
        payment.transaction_id = transaction.id

    except Exception as e:
        print(f"Error creating payment transaction: {str(e)}")
        raise

# Interface Routes
@invoices_bp.route('/status_types', methods=['GET'])
def get_status_types():
    """Get all valid invoice status types"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(INVOICE_STATUSES)

@invoices_bp.route('/next_number', methods=['GET'])
def get_next_number():
    """Get the next available invoice number"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'invoice_no': get_next_invoice_number()})

# Operations Routes
@invoices_bp.route('/create_invoice', methods=['POST'])
def create_invoice():
    """Create a new invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Generate invoice ID
        data['id'] = generate_invoice_id()
        
        line_items = [LineItem(
            product_id=item['product_id'],
            description=item['description'],
            unit_price=float(item['unit_price']),
            quantity=float(item['quantity'])
        ) for item in data['line_items']]

        # Create new invoice instance
        invoice = Invoice(
            id=data['id'],
            customer_id=data['customer_id'],
            customer_name=data['customer_name'],
            date=data['date'],
            due_date=data['due_date'],
            payment_terms=data['payment_terms'],
            status=data['status'],
            line_items=line_items,
            total=data['total'],
            balance_due=data['balance_due'],
            notes=data.get('notes', ''),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
        
        invoices_data = load_invoices(uid)
        invoices = invoices_data.get('invoices', [])
        
        # Add new invoice
        invoice_dict = invoice.to_dict()
        invoices.append(invoice_dict)
        
        # Save updated invoices
        save_invoices(uid, {'invoices': invoices})

        transaction = create_invoice_transaction(invoice, uid)
        if transaction:
            transactions_data = Transaction.load_user_transactions(uid)
            transactions_data['transactions'].append(transaction)
            Transaction.save_user_transactions(uid, transactions_data)

            if invoice.status in ['sent', 'paid']:
                post_transaction(transaction['id'], uid)
        
        return jsonify(invoice_dict), 200
        
    except Exception as e:
        print(f"Error creating invoice: {e}")
        return jsonify({"error": str(e)}), 400

@invoices_bp.route('/update_invoice/<id>', methods=['PUT'])
def update_invoice(id):
    """Update an invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        # Load all invoices
        invoices_data = load_invoices(uid)
        
        # Get the invoices list from the data structure
        if isinstance(invoices_data, dict) and 'invoices' in invoices_data:
            invoices = invoices_data['invoices']
        else:
            return jsonify({'error': 'Invalid invoices data structure'}), 500
        
        # Find the invoice to update
        invoice_index = None
        for i, inv in enumerate(invoices):
            if inv['id'] == id:
                invoice_index = i
                break
                
        if invoice_index is None:
            return jsonify({'error': 'Invoice not found'}), 404
            
        current_invoice = invoices[invoice_index]
        if current_invoice['status'] not in ['draft', 'sent']:
            return jsonify({'error': 'Cannot update a paid, void, or cancelled invoice'}), 400
        
        # Update the invoice with new data
        updated_invoice = {**current_invoice, **data}
        updated_invoice['updated_at'] = datetime.utcnow().isoformat()
        
        # Update in the list and save
        invoices[invoice_index] = updated_invoice
        
        # Save back with the same structure
        invoices_data['invoices'] = invoices
        save_invoices(uid, invoices_data)

        update_invoice_transaction(updated_invoice, f'invoice_{updated_invoice["status"]}')

        return jsonify(updated_invoice)
        
    except Exception as e:
        print(f"Error in update_invoice: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@invoices_bp.route('/get_invoice/<id>', methods=['GET'])
def get_invoice(id):
    """Get invoice by ID"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        invoice = Invoice.get_by_id(uid, id)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        return jsonify(invoice.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@invoices_bp.route('/list_invoices', methods=['GET'])
def list_invoices():
    """Get all invoices with optional filters"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        print(f"UID: {uid}")  
        invoices = Invoice.get_all(uid)
        print(f"Raw invoices: {invoices}")
        
        # Apply filters if provided
        status = request.args.get('status')
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
            
        customer = request.args.get('customer')
        if customer:
            invoices = [inv for inv in invoices if customer.lower() in inv.customer_name.lower()]
            
        # Convert to dict for response
        invoices_dict = [inv.to_dict() for inv in invoices]
        print(f"Response invoices: {invoices_dict}")  

        return jsonify({'invoices': invoices_dict})
    except Exception as e:
        print(f"Error in list_invoices: {str(e)}")  
        return jsonify({'error': str(e)}), 400

@invoices_bp.route('/delete_invoice/<id>', methods=['DELETE'])
def delete_invoice(id):
    """Delete an invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        invoice = Invoice.get_by_id(uid, id)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
            
        if invoice.status not in ['draft', 'void']:
            return jsonify({'error': 'Only draft or void invoices can be deleted'}), 400
            
        # Delete invoice
        invoice.delete(uid)
        
        # Delete associated transaction
        delete_invoice_transaction(invoice.id, uid)
        
        return jsonify({'message': 'Invoice deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@invoices_bp.route('/void/<id>', methods=['POST'])
def void_invoice(id):
    """Void an invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        void_reason = data.get('void_reason', '')
        
        invoice = Invoice.get_by_id(uid, id)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
            
        if invoice.status == 'void':
            return jsonify({'error': 'Invoice is already voided'}), 400
            
        invoice.status = 'void'
        invoice.void_reason = void_reason
        invoice.voided_at = datetime.utcnow().isoformat() 
        invoice.save(uid)
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @invoices_bp.route('/post/<id>', methods=['POST'])
# def post_invoice(id):
#     """Post an invoice, making it final"""
#     uid = get_user_id()
#     if not uid:
#         return jsonify({'error': 'Unauthorized'}), 401

#     try:
#         invoice = Invoice.get_by_id(uid, id)
#         if not invoice:
#             return jsonify({'error': 'Invoice not found'}), 404
            
#         if invoice.status != 'draft':
#             return jsonify({'error': 'Only draft invoices can be posted'}), 400
            
#         # Update status and save
#         invoice.status = 'posted'
#         invoice.save(uid)
        
#         # Update transaction
#         update_invoice_transaction(invoice.to_dict(), 'invoice_posted')
        
#         return jsonify(invoice.to_dict()), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@invoices_bp.route('/send/<id>', methods=['POST'])
def send_invoice(id):
    """Mark invoice as sent to customer"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load invoice with error handling
        try:
            invoice = Invoice.get_by_id(uid, id)
        except Exception as e:
            return jsonify({'error': f'Failed to load invoice: {str(e)}'}), 500

        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
            
        if invoice.status != 'draft':
            return jsonify({'error': 'Only draft invoices can be sent'}), 400
            
        # Update invoice
        invoice.status = 'sent'
        invoice.sent_at = datetime.utcnow().isoformat()
        
        # Save with error handling
        try:
            invoice.save(uid)
        except Exception as e:
            return jsonify({'error': f'Failed to save invoice: {str(e)}'}), 500
        
        # Convert to dict with error handling
        try:
            return jsonify(invoice.to_dict()), 200
        except Exception as e:
            return jsonify({'error': f'Failed to convert invoice to dict: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@invoices_bp.route('/duplicate/<id>', methods=['POST'])
def duplicate_invoice(id):
    """Create a copy of an existing invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load original invoice
        original = Invoice.load(id, uid)
        if not original:
            return jsonify({'error': 'Invoice not found'}), 404
            
        # Create new invoice data
        new_invoice_data = original.to_dict()
        
        # Update fields for new invoice
        new_invoice_data.update({
            'id': generate_invoice_id(),
            'invoice_no': get_next_invoice_number(),
            'status': 'draft'
        })
        
        # Remove fields that shouldn't be copied
        fields_to_remove = ['sent_at', 'paid_at', 'cancelled_at', 'payments']
        for field in fields_to_remove:
            new_invoice_data.pop(field, None)
            
        # Create and save new invoice
        new_invoice = Invoice.from_dict(new_invoice_data)
        new_invoice.save(uid)
        
        return jsonify(new_invoice.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@invoices_bp.route('/<id>/payments', methods=['GET'])
def get_payments(id):
    """Get all payments for an invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        invoice = Invoice.get_by_id(uid, id)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
            
        payments = [Payment.from_dict(p).to_dict() for p in invoice.payments]
        return jsonify(payments), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<id>/add_payment', methods=['POST'])
def add_payment(id):
    """Add a payment to an invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        invoices_data = load_invoices(uid)
        invoices = invoices_data.get('invoices', [])
        
        # Find the invoice
        invoice = None
        for inv in invoices:
            if inv['id'] == id:
                invoice = inv
                break
                
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404

        data = request.get_json()
        amount = float(data.get('amount', 0))
        payment_date = data.get('date', datetime.utcnow().isoformat())
        payment_method = data.get('payment_method', '')
        notes = data.get('notes', '')

        if 'payments' not in invoice:
            invoice['payments'] = []

        # Add new payment
        payment = {
            'amount': amount,
            'date': payment_date,
            'payment_method': payment_method,
            'notes': notes
        }
        invoice['payments'].append(payment)

        # Update balance due
        invoice['balance_due'] = invoice['total'] - sum(p['amount'] for p in invoice['payments'])
        invoice['last_payment_date'] = payment_date

        # Save updated invoices
        save_invoices(uid, invoices_data)

        # Update summary
        update_summary(invoices)

        create_payment_transaction(invoice, payment, uid)

        return jsonify(invoice), 200

    except Exception as e:
        print(f"Error in add_payment: {str(e)}")  # Add debugging
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/update_summary', methods=['POST'])
def update_summary_route():
    """Update invoices summary"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = load_invoices(uid)
        if not data or 'invoices' not in data:
            return jsonify({'error': 'No invoices data found'}), 404
            
        summary = update_summary(data['invoices'])
        data['summary'] = summary.to_dict()
        save_invoices(uid, data)
        return jsonify(summary.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 400

@invoices_bp.route('/get_summary', methods=['GET'])
def get_summary():
    """Get invoices summary"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = load_invoices(uid)
        if not data or 'invoices' not in data:
            return jsonify({'error': 'No invoices data found'}), 404
            
        summary = update_summary(data['invoices'])
        return jsonify(summary.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400