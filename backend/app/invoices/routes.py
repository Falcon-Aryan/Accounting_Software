from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta
import random

from . import invoices_bp
from .models import Invoice, InvoicesSummary, Payment, INVOICE_STATUSES, PAYMENT_METHODS, PAYMENT_TERMS
from app.transactions.models import Transaction, TransactionType, TransactionSubType, TransactionEntry
from app.chart_of_accounts.models import Account
from app.transactions.routes import create_transaction_direct, load_transactions, save_transactions
from app.chart_of_accounts.routes import load_chart_of_accounts
from app.products.routes import load_products

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INVOICES_FILE = os.path.join(DATA_DIR, 'invoices.json')

# Get account IDs from chart of accounts
def get_system_accounts():
    accounts = load_chart_of_accounts().get('accounts', [])
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

# Initialize system accounts
try:
    system_accounts = get_system_accounts()
    ACCOUNTS_RECEIVABLE_ID = system_accounts['ACCOUNTS_RECEIVABLE_ID']
    ACCOUNTS_PAYABLE_ID = system_accounts['ACCOUNTS_PAYABLE_ID']
    SALES_REVENUE_ID = system_accounts['SALES_REVENUE_ID']
    COGS_ID = system_accounts['COGS_ID']
    INVENTORY_ASSET_ID = system_accounts['INVENTORY_ASSET_ID']
    CASH_AND_BANK_ID = system_accounts['CASH_AND_BANK_ID']
except Exception as e:
    print(f"Error loading system accounts: {str(e)}")
    # Fallback values in case of error - these should match your chart of accounts
    ACCOUNTS_RECEIVABLE_ID = "1100-0001"  # Accounts Receivable
    ACCOUNTS_PAYABLE_ID = "2100-0001"     # Accounts Payable
    SALES_REVENUE_ID = "4000-0001"        # Sales Revenue
    COGS_ID = "5000-0001"                 # Cost of Goods Sold
    INVENTORY_ASSET_ID = "1200-0001"      # Inventory Asset
    CASH_AND_BANK_ID = "1000-0001"        # Cash and Bank

def deep_update(original: Dict, update: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def load_invoices() -> Dict:
    """Load invoices data from JSON file"""
    try:
        if os.path.exists(INVOICES_FILE):
            with open(INVOICES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading invoices data: {str(e)}")
    return {'invoices': [], 'summary': {}}

def save_invoices(data: Dict) -> bool:
    """Save invoices data to JSON file"""
    try:
        with open(INVOICES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving invoices data: {str(e)}")
        return False

def update_summary(invoices: List[Dict]) -> InvoicesSummary:
    """Update invoices summary information"""
    summary = InvoicesSummary()
    
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
        elif invoice['status'] == 'posted':
            summary.posted_count += 1
            summary.posted_amount += balance_due
        elif invoice['status'] == 'paid':
            summary.paid_count += 1
            summary.paid_amount += invoice['total_amount']  # Use total amount for historical tracking
        elif invoice['status'] == 'overdue':
            summary.overdue_count += 1
            summary.overdue_amount += balance_due
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
    """Calculate due date based on payment terms"""
    invoice_date = datetime.fromisoformat(invoice_date)
    if payment_terms == 'net_15':
        due_date = invoice_date + timedelta(days=15)
    elif payment_terms == 'net_30':
        due_date = invoice_date + timedelta(days=30)
    elif payment_terms == 'net_60':
        due_date = invoice_date + timedelta(days=60)
    else:  # due_on_receipt or custom
        due_date = invoice_date
    return due_date.isoformat()

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
        print(f"Creating invoice transaction for invoice {invoice_data.get('invoice_no')}")
        print(f"Products: {json.dumps(invoice_data.get('products', []), indent=2)}")
        
        # Calculate total amount
        total_amount = sum(float(p.get('price', 0)) * float(p.get('quantity', 0)) 
                          for p in invoice_data.get('products', []))
        print(f"Total amount: {total_amount}")

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
        for product in invoice_data.get('products', []):
            print(f"Processing product: {product.get('name')}")
            print(f"Product type: {product.get('type')}")
            print(f"Product cost price: {product.get('cost_price')}")
            if product.get('type') == 'inventory_item':
                print("Found inventory item!")
                cost_price = float(product.get('cost_price', 0))
                quantity = float(product.get('quantity', 0))
                cost_amount = cost_price * quantity
                total_cost += cost_amount
                print(f"Cost amount for {product.get('name')}: {cost_amount}")
        
        print(f"Total cost: {total_cost}")
        if total_cost > 0:
            print("Adding COGS entries")
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
        
        print(f"Final entries: {json.dumps(entries, indent=2)}")
        
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
            'products': invoice_data.get('products', []),
            'entries': entries,
            'amount': total_amount
        }
        create_transaction_direct(transaction_data)
    except Exception as e:
        print(f"Error creating invoice transaction: {str(e)}")
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
    """Delete the transaction record for an invoice"""
    try:
        transactions = load_transactions()
        transactions['transactions'] = [t for t in transactions['transactions'] 
                                     if not (t.get('reference_type') == 'invoice' and 
                                           t.get('reference_id') == invoice_id)]
        save_transactions(transactions)
    except Exception as e:
        print(f"Error deleting invoice transaction: {str(e)}")
        raise

# Interface Routes
@invoices_bp.route('/status_types', methods=['GET'])
def get_status_types():
    """Get all valid invoice status types"""
    return jsonify(INVOICE_STATUSES)

@invoices_bp.route('/next_number', methods=['GET'])
def get_next_number():
    """Get the next available invoice number"""
    return jsonify({'invoice_no': get_next_invoice_number()})

# Operations Routes
@invoices_bp.route('/create_invoice', methods=['POST'])
def create_invoice():
    """Create a new invoice"""
    try:
        data = request.get_json()
        
        # Load invoice data
        invoices_data = load_invoices()
        
        # Generate invoice ID and number
        invoice_id = generate_invoice_id()
        while not is_id_unique(invoice_id, invoices_data['invoices']):
            invoice_id = generate_invoice_id()
            
        data['id'] = invoice_id
        data['invoice_no'] = get_next_invoice_number()
        
        # Set dates and status
        data['invoice_date'] = data.get('invoice_date', datetime.utcnow().date().isoformat())
        data['due_date'] = data.get('due_date') or calculate_due_date(data.get('invoice_date'), data.get('payment_terms', 'due_on_receipt'))
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = data['created_at']
        data['status'] = 'draft'  # Always start as draft
        data['payments'] = []
        data['last_payment_date'] = None
        
        # Load product details to get correct type and cost price
        products_data = load_products()
        products_dict = {p['id']: p for p in products_data.get('products', [])}
        
        # Update products with full details
        for product in data.get('products', []):
            if product.get('id') in products_dict:
                full_product = products_dict[product['id']]
                product['type'] = full_product.get('type', 'service')
                product['cost_price'] = full_product.get('cost_price', 0)
        
        # Calculate total amount and balance due
        total_amount = sum(float(product.get('price', 0)) * float(product.get('quantity', 0)) 
                          for product in data.get('products', []))
        data['total_amount'] = total_amount
        data['balance_due'] = total_amount
        
        # Create invoice object and validate
        invoice = Invoice.from_dict(data)
        
        # Create draft transaction
        create_invoice_transaction(data, sub_type='invoice_draft')
        
        # Save invoice
        invoices_data['invoices'].append(invoice.to_dict())
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save invoice'}), 500
            
        return jsonify(invoice.to_dict()), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating invoice: {str(e)}'}), 500

@invoices_bp.route('/update_invoice/<id>', methods=['PATCH'])
def update_invoice(id):
    """Update an invoice"""
    try:
        data = request.get_json()
        
        # Load invoices data
        invoices_data = load_invoices()
        
        # Find the invoice
        invoice = next((inv for inv in invoices_data['invoices'] if inv['id'] == id), None)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
            
        # Check if invoice can be edited
        if invoice['status'] not in ['draft']:
            return jsonify({'message': f"Cannot edit invoice with status '{invoice['status']}'. Only draft invoices can be edited."}), 400
            
        # Update invoice data
        invoice.update(data)
        invoice['updated_at'] = datetime.utcnow().isoformat()
        
        # Update transaction
        update_invoice_transaction(invoice, sub_type='invoice_draft')
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        # Save changes
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save invoice'}), 500
            
        return jsonify(invoice), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating invoice: {str(e)}'}), 500

@invoices_bp.route('/delete_invoice/<string:id>', methods=['DELETE'])
def delete_invoice(id):
    """Delete an invoice"""
    try:
        # Load invoice data
        invoices_data = load_invoices()
        
        # Find invoice
        invoice = None
        for i, inv in enumerate(invoices_data['invoices']):
            if inv['id'] == id:
                invoice = inv
                invoices_data['invoices'].pop(i)
                break
                
        if invoice is None:
            return jsonify({'message': 'Invoice not found'}), 404
            
        # Delete associated transaction
        delete_invoice_transaction(id)
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save invoice data'}), 500
            
        return jsonify({'message': 'Invoice deleted successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Error deleting invoice: {str(e)}'}), 500

@invoices_bp.route('/get_invoice/<string:id>', methods=['GET'])
def get_invoice(id):
    """Get invoice by ID"""
    try:
        data = load_invoices()
        invoice = next(
            (inv for inv in data.get('invoices', []) if inv.get('id') == id),
            None
        )
        
        if invoice:
            return jsonify(invoice)
        else:
            return jsonify({'message': 'Invoice not found'}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@invoices_bp.route('/list_invoices', methods=['GET'])
def list_invoices():
    """Get all invoices with optional filters"""
    try:
        # Get query parameters
        status = request.args.get('status')
        search = request.args.get('search', '').lower()
        
        # Load data
        data = load_invoices()
        invoices = data.get('invoices', [])
        
        # Apply filters
        if status and status != 'All':
            invoices = [inv for inv in invoices if inv.get('status') == status]
            
        if search:
            invoices = [
                inv for inv in invoices 
                if search in inv.get('customer_name', '').lower() or 
                   search in inv.get('invoice_no', '').lower()
            ]
            
        return jsonify({
            'invoices': invoices,
            'summary': update_summary(invoices).to_dict()
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@invoices_bp.route('/get_summary', methods=['GET'])
def get_summary():
    """Get invoices summary"""
    try:
        data = load_invoices()
        invoices = data.get('invoices', [])
        summary = update_summary(invoices)
        return jsonify(summary.to_dict())
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@invoices_bp.route('/<string:id>/add_payment', methods=['POST', 'OPTIONS'])
def add_payment(id):
    """Add a payment to an invoice"""
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        payment_data = request.get_json()
        print(f"Received payment data: {json.dumps(payment_data, indent=2)}")
        
        # Load invoice
        invoices_data = load_invoices()
        invoice = next((inv for inv in invoices_data['invoices'] if inv['id'] == id), None)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
            
        # Generate payment ID
        payment_id = generate_payment_id()
        payment_data['id'] = payment_id
        
        # Convert amount to float
        payment_data['amount'] = float(payment_data['amount'])
        
        # Set payment date
        payment_data['date'] = payment_data.get('payment_date', datetime.utcnow().isoformat())
            
        # Create payment object
        payment = Payment.from_dict(payment_data)
        
        # Validate payment amount
        if payment.amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
            
        # Calculate remaining balance
        total_paid = sum(float(p.get('amount', 0)) for p in invoice.get('payments', []))
        remaining_balance = float(invoice['total_amount']) - total_paid
        
        if payment.amount > remaining_balance:
            raise ValueError(f"Payment amount ({payment.amount}) exceeds remaining balance ({remaining_balance})")

        # Validate accounts
        cash_account = validate_account_id(CASH_AND_BANK_ID, 'asset')
        if not cash_account:
            raise ValueError("Invalid Cash account")
            
        ar_account = validate_account_id(ACCOUNTS_RECEIVABLE_ID, 'asset')
        if not ar_account:
            raise ValueError("Invalid Accounts Receivable account")

        # Create payment transaction
        transaction_data = {
            'date': payment.date,
            'description': f"Payment for Invoice {invoice['invoice_no']}",
            'transaction_type': TransactionType.PAYMENT_RECEIVED.value,
            'sub_type': TransactionSubType.CASH_PAYMENT.value,
            'reference_type': 'invoice_payment',
            'reference_id': f"{id}_{payment_id}",
            'customer_name': invoice.get('customer_name'),
            'entries': [
                {
                    'accountId': cash_account,
                    'amount': payment.amount,
                    'type': 'debit',
                    'description': f"Cash Receipt - Invoice {invoice['invoice_no']}"
                },
                {
                    'accountId': ar_account,
                    'amount': payment.amount,
                    'type': 'credit',
                    'description': f"Payment Applied - Invoice {invoice['invoice_no']}"
                }
            ],
            'amount': payment.amount,
            'status': 'posted'  # Payments are always posted immediately
        }
        
        # Create the transaction
        transaction_response = create_transaction_direct(transaction_data)
        if not isinstance(transaction_response, dict):
            raise ValueError("Failed to create payment transaction")
            
        payment.transaction_id = transaction_response.get('id')
        
        # Add payment to invoice
        if 'payments' not in invoice:
            invoice['payments'] = []
        invoice['payments'].append(payment.to_dict())
        
        # Update balance due
        invoice['balance_due'] = float(invoice['total_amount']) - (total_paid + payment.amount)
        
        # Update last payment date
        invoice['last_payment_date'] = payment.date
        
        # Update invoice status
        check_and_update_status(invoice)
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save payment'}), 500
            
        return jsonify(payment.to_dict()), 201
        
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        print(f"Error adding payment: {str(e)}")
        return jsonify({'message': f'Error adding payment: {str(e)}'}), 500

@invoices_bp.route('/get_payments/<string:id>', methods=['GET'])
def get_payments(id):
    """Get all payments for an invoice"""
    try:
        invoices_data = load_invoices()
        invoice = next((inv for inv in invoices_data['invoices'] if inv['id'] == id), None)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
            
        return jsonify({
            "payments": invoice.get('payments', []),
            "total_paid": sum(payment['amount'] for payment in invoice.get('payments', [])),
            "balance_due": invoice['balance_due']
        }), 200
        
    except Exception as e:
        print(f"Error getting payments: {str(e)}")
        return jsonify({"error": "Failed to get payments"}), 500

@invoices_bp.route('/void_invoice/<string:id>', methods=['POST'])
def void_invoice(id):
    """Void an invoice"""
    try:
        # Load invoices data
        invoices_data = load_invoices()
        if not invoices_data or 'invoices' not in invoices_data:
            return jsonify({
                'message': 'No invoices data found',
                'error_code': 'NO_INVOICES_DATA'
            }), 404
            
        # Find invoice
        invoice = None
        for inv in invoices_data['invoices']:
            if inv.get('id') == id:
                invoice = inv
                break
                
        if invoice is None:
            return jsonify({
                'message': f'Invoice with ID {id} not found',
                'error_code': 'INVOICE_NOT_FOUND'
            }), 404
            
        # Check if invoice is already voided
        if invoice.get('status', '').lower() == 'void':
            return jsonify({
                'message': f'Invoice {invoice.get("invoice_no")} is already voided',
                'error_code': 'ALREADY_VOIDED'
            }), 400
            
        # Create void transaction
        try:
            # Group products by income accounts for consolidated entries
            income_totals = {}
            for product in invoice['products']:
                income_account = validate_account_id(
                    product.get('income_account_id', SALES_REVENUE_ID),
                    'income'
                )
                amount = float(product['price']) * float(product['quantity'])
                income_totals[income_account] = income_totals.get(income_account, 0) + amount

            # Create void transaction entries
            void_entries = []
            
            # Add debit entries for each income account (reverse the credits)
            for account_id, amount in income_totals.items():
                void_entries.append({
                    'accountId': account_id,
                    'amount': amount,
                    'type': 'debit',
                    'description': f"Void - Sales Revenue - Invoice {invoice.get('invoice_no')}"
                })

            # Add credit entry to AR (reverse the debit)
            void_entries.append({
                'accountId': ACCOUNTS_RECEIVABLE_ID,
                'amount': invoice.get('total_amount', 0),
                'type': 'credit',
                'description': f"Void - Accounts Receivable - Invoice {invoice.get('invoice_no')}"
            })

            # Create the void transaction
            void_transaction = {
                'date': datetime.utcnow().date().isoformat(),
                'description': f"Void Invoice {invoice.get('invoice_no')}",
                'transaction_type': TransactionType.INVOICE.value,
                'reference_type': 'invoice_void',
                'reference_id': f"{id}_void",
                'status': 'posted',
                'customer_name': invoice.get('customer_name'),
                'products': invoice.get('products', []),
                'entries': void_entries,
                'amount': invoice.get('total_amount', 0),
                'void_reason': request.get_json().get('reason', 'User requested void')
            }
            
            # Create the void transaction
            create_transaction_direct(void_transaction)
            
            # Find and void the original transaction
            transactions_data = load_transactions()
            if transactions_data and 'transactions' in transactions_data:
                for transaction in transactions_data['transactions']:
                    if (transaction['reference_type'] == 'invoice' 
                        and transaction['reference_id'] == id 
                        and transaction['transaction_type'] == TransactionType.INVOICE.value
                        and transaction['status'] != 'void'):
                        transaction['status'] = 'void'
                        transaction['voided_at'] = datetime.utcnow().isoformat()
                        transaction['voided_by'] = 'system'
                        transaction['void_reason'] = request.get_json().get('reason', 'User requested void')
                
                save_transactions(transactions_data)
            
            # Update invoice status
            invoice['status'] = 'void'
            invoice['voided_at'] = datetime.utcnow().isoformat()
            invoice['updated_at'] = datetime.utcnow().isoformat()
            invoice['void_reason'] = request.get_json().get('reason', 'User requested void')
            
            # Save changes
            invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
            if not save_invoices(invoices_data):
                return jsonify({
                    'message': 'Failed to save voided invoice',
                    'error_code': 'SAVE_FAILED'
                }), 500
                
            return jsonify(invoice), 200
            
        except Exception as e:
            print(f"Error voiding invoice transaction: {str(e)}")
            return jsonify({
                'message': f'Error voiding invoice transaction: {str(e)}',
                'error_code': 'VOID_TRANSACTION_ERROR'
            }), 500
            
    except Exception as e:
        print(f"Error voiding invoice: {str(e)}")
        return jsonify({
            'message': f'Error voiding invoice: {str(e)}',
            'error_code': 'VOID_ERROR'
        }), 500

@invoices_bp.route('/post_invoice/<id>', methods=['POST'])
def post_invoice(id):
    """Post an invoice, making it final and creating official journal entries"""
    try:
        # Load invoices data
        invoices_data = load_invoices()
        
        # Find the invoice
        invoice = next((inv for inv in invoices_data['invoices'] if inv['id'] == id), None)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
            
        # Check if invoice can be posted
        if invoice['status'] != 'draft':
            return jsonify({'message': f"Cannot post invoice with status '{invoice['status']}'. Only draft invoices can be posted."}), 400
            
        # Update invoice status and create official transaction
        invoice['status'] = 'posted'
        invoice['updated_at'] = datetime.utcnow().isoformat()
        
        # Create posted transaction (this will replace the draft transaction)
        create_invoice_transaction(invoice, sub_type='invoice_posted')
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        # Save changes
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save invoice'}), 500
            
        return jsonify(invoice), 200
        
    except Exception as e:
        return jsonify({'message': f'Error posting invoice: {str(e)}'}), 500
