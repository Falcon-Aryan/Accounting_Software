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
from app.transactions.routes import create_transaction_direct, load_transactions, save_transactions, post_transaction
from app.chart_of_accounts.routes import load_chart_of_accounts
from app.products.routes import load_products

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
            'ACCOUNTS_RECEIVABLE_ID': ar_account['id'],
            'ACCOUNTS_PAYABLE_ID': ap_account['id'],
            'SALES_REVENUE_ID': sales_account['id'],
            'COGS_ID': cogs_account['id'],
            'INVENTORY_ASSET_ID': inventory_account['id'],
            'CASH_AND_BANK_ID': cash_account['id']
        }
    except Exception as e:
        # Fallback values in case of error - these should match your chart of accounts
        return {
            'ACCOUNTS_RECEIVABLE_ID': "1100-0001",  # Accounts Receivable
            'ACCOUNTS_PAYABLE_ID': "2100-0001",     # Accounts Payable
            'SALES_REVENUE_ID': "4000-0001",        # Sales Revenue
            'COGS_ID': "5000-0001",                 # Cost of Goods Sold
            'INVENTORY_ASSET_ID': "1200-0001",      # Inventory Asset
            'CASH_AND_BANK_ID': "1000-0001"         # Cash and Bank
        }

# Initialize system accounts with fallback values
system_accounts = get_system_accounts()  # Don't pass uid during module initialization
ACCOUNTS_RECEIVABLE_ID = system_accounts['ACCOUNTS_RECEIVABLE_ID']
ACCOUNTS_PAYABLE_ID = system_accounts['ACCOUNTS_PAYABLE_ID']
SALES_REVENUE_ID = system_accounts['SALES_REVENUE_ID']
COGS_ID = system_accounts['COGS_ID']
INVENTORY_ASSET_ID = system_accounts['INVENTORY_ASSET_ID']
CASH_AND_BANK_ID = system_accounts['CASH_AND_BANK_ID']

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
        data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()
        
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
        balance_due = invoice['total_amount'] - total_paid
        
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
            summary.paid_amount += invoice['total_amount']
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
    invoice['balance_due'] = invoice['total_amount'] - total_paid
    
    if total_paid >= invoice['total_amount']:
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

def create_invoice_transaction(invoice_data: Dict, sub_type: str = 'invoice_draft') -> None:
    """Create a transaction record for an invoice"""
    try:
        # Calculate total amount
        total_amount = sum(float(item.get('unit_price', 0)) * float(item.get('quantity', 0)) 
                          for item in invoice_data.get('line_items', []))

        # Create entries list
        entries = []
        
        # Add revenue entries
        entries.extend([
            {
                'accountId': ACCOUNTS_RECEIVABLE_ID,
                'amount': total_amount,
                'type': 'debit',
                'description': f"Invoice {invoice_data['invoice_no']} - Revenue"
            },
            {
                'accountId': SALES_REVENUE_ID,
                'amount': total_amount,
                'type': 'credit',
                'description': f"Invoice {invoice_data['invoice_no']} - Revenue"
            }
        ])
        
        # Add COGS entries only for inventory items
        total_cost = 0
        for item in invoice_data.get('line_items', []):
            if item.get('type') == 'inventory_item':
                cost_price = float(item.get('cost_price', 0))
                quantity = float(item.get('quantity', 0))
                cost_amount = cost_price * quantity
                total_cost += cost_amount
        
        if total_cost > 0:
            entries.extend([
                {
                    'accountId': COGS_ID,
                    'amount': total_cost,
                    'type': 'debit',
                    'description': f"Invoice {invoice_data['invoice_no']} - Cost of Goods Sold"
                },
                {
                    'accountId': INVENTORY_ASSET_ID,
                    'amount': total_cost,
                    'type': 'credit',
                    'description': f"Invoice {invoice_data['invoice_no']} - Inventory Reduction"
                }
            ])
        
        # Create transaction
        transaction_data = {
            'date': invoice_data['invoice_date'],
            'description': f"Invoice {invoice_data['invoice_no']} created",
            'transaction_type': TransactionType.INVOICE.value,
            'sub_type': sub_type,
            'reference_type': 'invoice',
            'reference_id': invoice_data['id'],
            'status': 'draft',
            'customer_name': invoice_data.get('customer_name', ''),
            'line_items': invoice_data.get('line_items', []),
            'entries': entries,
            'amount': total_amount
        }
        create_transaction_direct(transaction_data)
    except Exception as e:
        print(f"Error in create_transaction_direct: {str(e)}")
        raise

def update_invoice_transaction(invoice_data: Dict, sub_type: str) -> None:
    """Update the transaction record for an invoice"""
    try:
        # Delete old transaction
        transactions = load_transactions()
        transactions['transactions'] = [t for t in transactions['transactions'] 
                                     if not (t.get('reference_type') == 'invoice' and 
                                           t.get('reference_id') == invoice_data['id'])]
        save_transactions(transactions)
        
        # Create new transaction
        create_invoice_transaction(invoice_data, sub_type)
    except Exception as e:
        print(f"Error updating invoice transaction: {str(e)}")
        raise

def delete_invoice_transaction(invoice_id: str) -> None:
    """Delete the transaction record for an invoice and its payments"""
    try:
        transactions = load_transactions()
        # Remove both invoice and payment transactions
        transactions['transactions'] = [t for t in transactions['transactions'] 
                                     if not ((t.get('reference_type') == 'invoice' and t.get('reference_id') == invoice_id) or
                                           (t.get('transaction_type') == TransactionType.PAYMENT_RECEIVED.value and 
                                            t.get('reference_id', '').startswith(f"{invoice_id}_")))]
        save_transactions(transactions)
    except Exception as e:
        print(f"Error deleting invoice transaction: {str(e)}")

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
        data = request.get_json()
        
        # Generate invoice ID and number
        invoice_id = generate_invoice_id()
        invoice_no = get_next_invoice_number()
        
        # Set dates
        invoice_date = data.get('invoice_date', datetime.utcnow().isoformat())
        payment_terms = data.get('payment_terms', 'due_on_receipt')
        due_date = calculate_due_date(invoice_date, payment_terms)

        # Create invoice instance
        invoice = Invoice(
            id=invoice_id,
            invoice_no=invoice_no,
            invoice_date=invoice_date,
            due_date=due_date,
            customer_name=data['customer_name'],
            status='draft',
            line_items=data['line_items'],
            payment_terms=data.get('payment_terms', 'due_on_receipt')
        )
        
        # Save invoice
        invoice.save(uid)
        
        # Create transaction record
        create_invoice_transaction(invoice.to_dict(), 'invoice_draft')
        
        return jsonify(invoice.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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
        
        # Update transaction if status changed
        if 'status' in data and data['status'] != current_invoice['status']:
            update_invoice_transaction(updated_invoice, f"invoice_{data['status']}")
        
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
        invoices = Invoice.get_all(uid)
        
        # Apply filters if provided
        status = request.args.get('status')
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
            
        customer = request.args.get('customer')
        if customer:
            invoices = [inv for inv in invoices if customer.lower() in inv.customer_name.lower()]
            
        # Convert to dict for response
        invoices_dict = [inv.to_dict() for inv in invoices]
        
        return jsonify({'invoices': invoices_dict})
    except Exception as e:
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
        delete_invoice_transaction(id)
        
        return jsonify({'message': 'Invoice deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400



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
            'invoice_date': datetime.utcnow().isoformat(),
            'due_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),  # Default 30 days
            'status': 'draft',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
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