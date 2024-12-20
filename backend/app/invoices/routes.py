from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta
import random

from . import invoices_bp
from .models import Invoice, InvoicesSummary, Payment, INVOICE_STATUSES, PAYMENT_METHODS, PAYMENT_TERMS
from app.transactions.models import Transaction, TransactionType, TransactionEntry
from app.chart_of_accounts.models import Account
from app.transactions.routes import create_transaction_direct, load_transactions, save_transactions

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INVOICES_FILE = os.path.join(DATA_DIR, 'invoices.json')

# Account IDs - These should match your chart of accounts
ACCOUNTS_RECEIVABLE_ID = "1200"  # Accounts Receivable
SALES_REVENUE_ID = "4000"        # Sales Revenue
CASH_AND_BANK_ID = "1000"        # Cash and Bank

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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
        elif invoice['status'] == 'sent':
            summary.sent_count += 1
            summary.sent_amount += balance_due
        elif invoice['status'] == 'partially_paid':
            summary.partially_paid_count += 1
            summary.partially_paid_amount += balance_due
        elif invoice['status'] == 'paid':
            summary.paid_count += 1
            summary.paid_amount += invoice['total_amount']  # Use total amount for historical tracking
        elif invoice['status'] == 'overdue':
            summary.overdue_count += 1
            summary.overdue_amount += balance_due
        elif invoice['status'] == 'void':
            summary.void_count += 1
            
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
    due_date = datetime.fromisoformat(invoice['due_date'].replace('Z', '+00:00'))
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

def calculate_due_date(payment_terms: str) -> str:
    """Calculate due date based on payment terms"""
    now = datetime.utcnow()
    if payment_terms == 'net_15':
        due_date = now + timedelta(days=15)
    elif payment_terms == 'net_30':
        due_date = now + timedelta(days=30)
    elif payment_terms == 'net_60':
        due_date = now + timedelta(days=60)
    else:  # due_on_receipt or custom
        due_date = now
    return due_date.isoformat()

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
        
        # Generate invoice ID and number
        invoice_id = generate_invoice_id()
        while not is_id_unique(invoice_id, load_invoices().get('invoices', [])):
            invoice_id = generate_invoice_id()
            
        data['id'] = invoice_id
        data['invoice_no'] = get_next_invoice_number()
        
        # Set dates
        data['invoice_date'] = data.get('invoice_date', datetime.utcnow().isoformat())
        data['due_date'] = data.get('due_date') or calculate_due_date(data.get('payment_terms', 'due_on_receipt'))
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = data['created_at']
        data['status'] = 'draft'
        data['payments'] = []
        
        # Create invoice object and validate
        invoice = Invoice.from_dict(data)
        
        # Save invoice
        invoices_data = load_invoices()
        invoices_data['invoices'].append(invoice.to_dict())
        
        # Create initial transaction when invoice is created (if not draft)
        if data.get('status') != 'draft':
            transaction_data = {
                'date': data['invoice_date'],
                'description': f"Invoice {data['invoice_no']} created",
                'transaction_type': TransactionType.INVOICE.value,
                'reference_type': 'invoice',
                'reference_id': invoice_id,
                'entries': [
                    {
                        'accountId': ACCOUNTS_RECEIVABLE_ID,
                        'amount': invoice.total_amount,
                        'type': 'debit',
                        'description': f"Accounts Receivable - Invoice {data['invoice_no']}"
                    },
                    {
                        'accountId': SALES_REVENUE_ID,
                        'amount': invoice.total_amount,
                        'type': 'credit',
                        'description': f"Sales Revenue - Invoice {data['invoice_no']}"
                    }
                ]
            }
            transaction_response = create_transaction_direct(transaction_data)
            
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save invoice'}), 500
            
        return jsonify(invoice.to_dict()), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating invoice: {str(e)}'}), 500

@invoices_bp.route('/update_invoice/<string:id>', methods=['PATCH'])
def update_invoice(id):
    """Update an invoice"""
    try:
        data = request.get_json()
        
        # Load invoice
        invoices_data = load_invoices()
        invoice_index = None
        invoice = None
        
        for i, inv in enumerate(invoices_data['invoices']):
            if inv['id'] == id:
                invoice_index = i
                invoice = inv
                break
                
        if invoice is None:
            return jsonify({'message': 'Invoice not found'}), 404
            
        # Check if amount is being modified
        old_amount = invoice.get('total_amount', 0)
        new_amount = data.get('total_amount', old_amount)
        amount_changed = abs(new_amount - old_amount) > 0.01  # Using 0.01 to handle floating point precision
        
        # Check if status is being changed from draft to active
        old_status = invoice.get('status', 'draft')
        new_status = data.get('status', old_status)
        becoming_active = old_status == 'draft' and new_status == 'posted'  # Only create transaction when status becomes 'posted'
        
        # Update invoice data
        deep_update(invoice, data)
        invoice['updated_at'] = datetime.utcnow().isoformat()
        
        # Create invoice object to validate
        invoice_obj = Invoice.from_dict(invoice)
        
        # Handle transaction modifications
        try:
            # Case 1: Invoice becoming active - create new transaction
            if becoming_active:
                transaction_data = {
                    'date': invoice['invoice_date'],
                    'description': f"Invoice {invoice['invoice_no']} posted",
                    'transaction_type': TransactionType.INVOICE.value,
                    'reference_type': 'invoice',
                    'reference_id': id,
                    'status': 'posted',  # Set status to posted immediately
                    'entries': [
                        {
                            'accountId': ACCOUNTS_RECEIVABLE_ID,
                            'amount': invoice['total_amount'],
                            'type': 'debit',
                            'description': f"Accounts Receivable - Invoice {invoice['invoice_no']}"
                        },
                        {
                            'accountId': SALES_REVENUE_ID,
                            'amount': invoice['total_amount'],
                            'type': 'credit',
                            'description': f"Sales Revenue - Invoice {invoice['invoice_no']}"
                        }
                    ]
                }
                # Create the transaction and handle any errors
                try:
                    response = create_transaction_direct(transaction_data)
                    if not isinstance(response, dict) or 'id' not in response:
                        print(f"Error creating transaction: {response}")
                        raise Exception("Failed to create transaction")
                except Exception as e:
                    print(f"Error creating transaction: {str(e)}")
                    raise Exception(f"Failed to create transaction: {str(e)}")
                
            # Case 2: Amount changed on active invoice - modify existing transaction
            elif amount_changed and old_status != 'draft':
                # Find existing transaction
                transactions_data = load_transactions()
                transaction = next(
                    (t for t in transactions_data['transactions'] 
                     if t['reference_type'] == 'invoice' and t['reference_id'] == id),
                    None
                )
                
                if transaction:
                    # Update transaction amounts
                    for entry in transaction['entries']:
                        if entry['accountId'] == ACCOUNTS_RECEIVABLE_ID:
                            entry['amount'] = new_amount
                        elif entry['accountId'] == SALES_REVENUE_ID:
                            entry['amount'] = new_amount
                            
                    transaction['updated_at'] = datetime.utcnow().isoformat()
                    save_transactions(transactions_data)
                    
            # Case 3: Invoice being voided - reverse the transaction
            if new_status == 'void' and old_status != 'void':
                transaction_data = {
                    'date': datetime.utcnow().isoformat(),
                    'description': f"Void Invoice {invoice['invoice_no']}",
                    'transaction_type': TransactionType.INVOICE.value,
                    'reference_type': 'invoice_void',
                    'reference_id': f"{id}_void",
                    'entries': []
                }
                
                # Create reverse entries with opposite debit/credit
                for entry in invoice.get('entries', []):
                    reversal_entry = {
                        'accountId': entry.get('accountId'),
                        'amount': entry.get('amount', 0),
                        'type': 'credit' if entry.get('type') == 'debit' else 'debit',
                        'description': f"Void - {entry.get('description', '')}"
                    }
                    transaction_data['entries'].append(reversal_entry)
                
                # Create the reversal transaction
                create_transaction_direct(transaction_data)
                
                # Mark original transaction as void
                transaction['status'] = 'void'
                transaction['voided_at'] = datetime.utcnow().isoformat()
                transaction['voided_by'] = 'system'
                save_transactions(transactions_data)
                    
        except Exception as e:
            print(f"Error handling transactions: {str(e)}")
            # Continue with invoice update even if transaction handling fails
            
        # Update invoice in data
        invoices_data['invoices'][invoice_index] = invoice
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save invoice'}), 500
            
        return jsonify(invoice_obj.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error updating invoice: {str(e)}'}), 500

@invoices_bp.route('/delete_invoice/<string:id>', methods=['DELETE'])
def delete_invoice(id):
    """Delete an invoice"""
    try:
        # Load invoices data
        invoices_data = load_invoices()
        if not invoices_data or 'invoices' not in invoices_data:
            return jsonify({
                'message': 'No invoices data found',
                'error_code': 'NO_INVOICES_DATA'
            }), 404
            
        # Find invoice
        invoice_index = None
        invoice = None
        
        for i, inv in enumerate(invoices_data['invoices']):
            if inv.get('id') == id:
                invoice_index = i
                invoice = inv
                break
                
        if invoice is None:
            return jsonify({
                'message': f'Invoice with ID {id} not found',
                'error_code': 'INVOICE_NOT_FOUND'
            }), 404
            
        # Only check for payments if invoice is not draft
        if invoice.get('status', '').lower() != 'draft':
            payments = invoice.get('payments', [])
            if payments:
                payment_amount = sum(payment.get('amount', 0) for payment in payments)
                return jsonify({
                    'message': f'Cannot delete invoice {invoice.get("invoice_no")} because it has {len(payments)} payment(s) totaling {payment_amount}. Please void the invoice instead.',
                    'error_code': 'HAS_PAYMENTS',
                    'payment_count': len(payments),
                    'payment_total': payment_amount
                }), 400
            
            # Handle transactions for non-draft invoices
            try:
                # Find and void existing invoice transaction
                transactions_data = load_transactions()
                if transactions_data and 'transactions' in transactions_data:
                    invoice_transaction = next(
                        (t for t in transactions_data['transactions'] 
                         if t.get('reference_type') == 'invoice' and t.get('reference_id') == id),
                        None
                    )
                    
                    if invoice_transaction:
                        # Create reversing transaction
                        reversal_data = {
                            'date': datetime.utcnow().isoformat(),
                            'description': f"Delete Invoice {invoice.get('invoice_no', '')}",
                            'transaction_type': TransactionType.INVOICE.value,
                            'reference_type': 'invoice_deletion',
                            'reference_id': f"{id}_deletion",
                            'entries': []
                        }
                        
                        # Create reverse entries with opposite debit/credit
                        for entry in invoice_transaction.get('entries', []):
                            reversal_entry = {
                                'accountId': entry.get('accountId'),
                                'amount': entry.get('amount', 0),
                                'type': 'credit' if entry.get('type') == 'debit' else 'debit',
                                'description': f"Delete - {entry.get('description', '')}"
                            }
                            reversal_data['entries'].append(reversal_entry)
                        
                        # Create the reversal transaction
                        create_transaction_direct(reversal_data)
                        
                        # Mark original transaction as void
                        invoice_transaction['status'] = 'void'
                        invoice_transaction['voided_at'] = datetime.utcnow().isoformat()
                        invoice_transaction['voided_by'] = 'system'
                        save_transactions(transactions_data)
                    
            except Exception as e:
                print(f"Error handling transactions during deletion: {str(e)}")
                # Continue with invoice deletion even if transaction handling fails
                
        # Remove invoice
        invoices_data['invoices'].pop(invoice_index)
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        # Save changes
        if not save_invoices(invoices_data):
            return jsonify({
                'message': 'Failed to save changes after deletion. Please try again.',
                'error_code': 'SAVE_FAILED'
            }), 500
            
        return jsonify({
            'message': f'Invoice {invoice.get("invoice_no", id)} deleted successfully',
            'invoice_no': invoice.get('invoice_no'),
            'id': id
        })
        
    except Exception as e:
        print(f"Error in delete_invoice: {str(e)}")
        return jsonify({
            'message': f'Error deleting invoice: {str(e)}',
            'error_code': 'UNKNOWN_ERROR'
        }), 500

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

@invoices_bp.route('/add_payment/<string:id>', methods=['POST'])
def add_payment(id):
    """Add a payment to an invoice"""
    try:
        payment_data = request.get_json()
        
        # Load invoice
        invoices_data = load_invoices()
        invoice = next((inv for inv in invoices_data['invoices'] if inv['id'] == id), None)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
            
        # Generate payment ID
        payment_id = generate_payment_id()
        payment_data['id'] = payment_id
        
        # Set payment date if not provided
        if 'date' not in payment_data:
            payment_data['date'] = datetime.utcnow().isoformat()
            
        # Create payment object
        payment = Payment.from_dict(payment_data)
        
        # Create payment transaction
        transaction_data = {
            'date': payment.date,
            'description': f"Payment for Invoice {invoice['invoice_no']}",
            'transaction_type': TransactionType.PAYMENT.value,
            'reference_type': 'invoice_payment',
            'reference_id': f"{id}_{payment_id}",
            'entries': [
                {
                    'accountId': CASH_AND_BANK_ID,
                    'amount': payment.amount,
                    'type': 'debit',
                    'description': f"Cash Receipt - Invoice {invoice['invoice_no']}"
                },
                {
                    'accountId': ACCOUNTS_RECEIVABLE_ID,
                    'amount': payment.amount,
                    'type': 'credit',
                    'description': f"Payment Applied - Invoice {invoice['invoice_no']}"
                }
            ]
        }
        
        # Create the transaction
        transaction_response = create_transaction_direct(transaction_data)
        if transaction_response.status_code == 201:
            transaction_data = transaction_response.get_json()
            payment.transaction_id = transaction_data.get('id')
        
        # Add payment to invoice
        if 'payments' not in invoice:
            invoice['payments'] = []
        invoice['payments'].append(payment.to_dict())
        
        # Update invoice status
        check_and_update_status(invoice)
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to save payment'}), 500
            
        return jsonify(payment.to_dict()), 201
        
    except Exception as e:
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
            # Find original invoice transaction
            transactions_data = load_transactions()
            invoice_transaction = None
            
            if transactions_data and 'transactions' in transactions_data:
                invoice_transaction = next(
                    (t for t in transactions_data['transactions'] 
                     if t.get('reference_type') == 'invoice' and t.get('reference_id') == id),
                    None
                )
            
            # If no transaction exists, create one first
            if not invoice_transaction:
                transaction_data = {
                    'date': invoice.get('invoice_date'),
                    'description': f"Invoice {invoice.get('invoice_no')} created",
                    'transaction_type': TransactionType.INVOICE.value,
                    'reference_type': 'invoice',
                    'reference_id': id,
                    'entries': [
                        {
                            'accountId': ACCOUNTS_RECEIVABLE_ID,
                            'amount': invoice.get('total_amount', 0),
                            'type': 'debit',
                            'description': f"Accounts Receivable - Invoice {invoice.get('invoice_no')}"
                        },
                        {
                            'accountId': SALES_REVENUE_ID,
                            'amount': invoice.get('total_amount', 0),
                            'type': 'credit',
                            'description': f"Sales Revenue - Invoice {invoice.get('invoice_no')}"
                        }
                    ]
                }
                invoice_transaction = create_transaction_direct(transaction_data)
                
            # Create void transaction
            void_data = {
                'date': datetime.utcnow().isoformat(),
                'description': f"Void Invoice {invoice.get('invoice_no', '')}",
                'transaction_type': TransactionType.INVOICE.value,
                'reference_type': 'invoice_void',
                'reference_id': f"{id}_void",
                'entries': []
            }
            
            # Create void entries with opposite debit/credit
            for entry in invoice_transaction.get('entries', []):
                void_entry = {
                    'accountId': entry.get('accountId'),
                    'amount': entry.get('amount', 0),
                    'type': 'credit' if entry.get('type') == 'debit' else 'debit',
                    'description': f"Void - {entry.get('description', '')}"
                }
                void_data['entries'].append(void_entry)
            
            # Create the void transaction
            create_transaction_direct(void_data)
            
            # Mark original transaction as void
            invoice_transaction['status'] = 'void'
            invoice_transaction['voided_at'] = datetime.utcnow().isoformat()
            invoice_transaction['voided_by'] = 'system'
            save_transactions(transactions_data)
                    
        except Exception as e:
            print(f"Error handling transactions during void: {str(e)}")
            # Continue with invoice void even if transaction handling fails
            
        # Update invoice status
        invoice['status'] = 'void'
        invoice['voided_at'] = datetime.utcnow().isoformat()
        invoice['updated_at'] = datetime.utcnow().isoformat()
        
        # Update summary
        invoices_data['summary'] = update_summary(invoices_data['invoices']).to_dict()
        
        # Save changes
        if not save_invoices(invoices_data):
            return jsonify({
                'message': 'Failed to save changes after voiding. Please try again.',
                'error_code': 'SAVE_FAILED'
            }), 500
            
        return jsonify({
            'message': f'Invoice {invoice.get("invoice_no", id)} voided successfully',
            'invoice_no': invoice.get('invoice_no'),
            'id': id
        })
        
    except Exception as e:
        print(f"Error in void_invoice: {str(e)}")
        return jsonify({
            'message': f'Error voiding invoice: {str(e)}',
            'error_code': 'UNKNOWN_ERROR'
        }), 500
