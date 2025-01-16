from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from firebase_admin import auth

from . import estimates_bp
from .models import Estimate, EstimatesSummary, ESTIMATE_STATUSES, PAYMENT_TERMS
from app.transactions.models import Transaction, TransactionType, TransactionSubType, TransactionEntry
from app.chart_of_accounts.models import Account
from app.transactions.routes import create_transaction_direct, load_transactions, save_transactions, post_transaction
from app.chart_of_accounts.routes import load_chart_of_accounts
from app.products.routes import load_products
from app.invoices.models import Invoice
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
        sales_account = next((acc for acc in accounts if acc['accountType'] == 'Income' and acc['isDefault']), None)
        
        if not all([ar_account, sales_account]):
            raise Exception("Required system accounts not found in chart of accounts")
            
        return {
            'ACCOUNTS_RECEIVABLE_ID': ar_account['id'],
            'SALES_REVENUE_ID': sales_account['id']
        }
    except Exception as e:
        # Fallback values in case of error - these should match your chart of accounts
        return {
            'ACCOUNTS_RECEIVABLE_ID': "1100-0001",  # Accounts Receivable
            'SALES_REVENUE_ID': "4000-0001"         # Sales Revenue
        }

# Initialize system accounts with fallback values
system_accounts = get_system_accounts()  # Don't pass uid during module initialization
ACCOUNTS_RECEIVABLE_ID = system_accounts['ACCOUNTS_RECEIVABLE_ID']
SALES_REVENUE_ID = system_accounts['SALES_REVENUE_ID']

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

def load_estimates(uid: str = None) -> Dict:
    """Load estimates data from JSON file"""
    try:
        if not uid:
            return {
                'estimates': [], 
                'summary': EstimatesSummary().to_dict(),
                'metadata': {
                    'lastUpdated': datetime.utcnow().isoformat(),
                    'createdAt': datetime.utcnow().isoformat()
                }
            }
            
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            'data', 
            uid, 
            'estimates.json'
        )
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Ensure all required fields exist
                if 'metadata' not in data:
                    data['metadata'] = {
                        'lastUpdated': datetime.utcnow().isoformat(),
                        'createdAt': datetime.utcnow().isoformat()
                    }
                if 'summary' not in data:
                    data['summary'] = EstimatesSummary().to_dict()
                if 'estimates' not in data:
                    data['estimates'] = []
                return data
                
        # If file doesn't exist, return default structure
        return {
            'estimates': [],
            'summary': EstimatesSummary().to_dict(),
            'metadata': {
                'lastUpdated': datetime.utcnow().isoformat(),
                'createdAt': datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        print(f"Error loading estimates data: {str(e)}")
        return {
            'estimates': [],
            'summary': EstimatesSummary().to_dict(),
            'metadata': {
                'lastUpdated': datetime.utcnow().isoformat(),
                'createdAt': datetime.utcnow().isoformat()
            }
        }

def save_estimates(uid: str, data: Dict) -> None:
    """Save estimates data to JSON file"""
    try:
        # Update summary before saving
        summary = update_summary(data['estimates'])
        data['summary'] = summary.to_dict()
        data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()
        
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            'data', 
            uid, 
            'estimates.json'
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error saving estimates data: {str(e)}")
        raise

def update_summary(estimates: List[Dict]) -> EstimatesSummary:
    """Update estimates summary information"""
    summary = EstimatesSummary()
    
    for estimate in estimates:
        amount = float(estimate.get('total', 0))
        
        if estimate['status'] == 'draft':
            summary.draft_count += 1
            summary.draft_amount += amount
        elif estimate['status'] == 'pending':
            summary.pending_count += 1
            summary.pending_amount += amount
        elif estimate['status'] == 'accepted':
            summary.accepted_count += 1
            summary.accepted_amount += amount
        elif estimate['status'] == 'declined':
            summary.declined_count += 1
            summary.declined_amount += amount
        elif estimate['status'] == 'expired':
            summary.expired_count += 1
            summary.expired_amount += amount
        elif estimate['status'] == 'converted':
            summary.converted_count += 1
            summary.converted_amount += amount
            
        # Update totals
        if estimate['status'] == 'converted':
            summary.total_converted += amount
    
    return summary

def get_next_estimate_number() -> str:
    """Generate the next estimate number"""
    data = load_estimates()
    estimates = data.get('estimates', [])
    if not estimates:
        return "EST-2025-001"
    
    current_year = datetime.now().year
    year_estimates = [est for est in estimates if est['estimate_no'].startswith(f"EST-{current_year}")]
    
    if not year_estimates:
        return f"EST-{current_year}-001"
    
    last_number = max(int(est['estimate_no'].split('-')[2]) for est in year_estimates)
    return f"EST-{current_year}-{(last_number + 1):03d}"

def generate_estimate_id() -> str:
    """Generate a random 8-digit ID with a dash in the middle"""
    # Generate two 4-digit numbers
    first_half = str(random.randint(1000, 9999))
    second_half = str(random.randint(1000, 9999))
    return f"{first_half}-{second_half}"

def is_id_unique(id: str, estimates: List[Dict]) -> bool:
    """Check if an ID is unique among existing estimates"""
    return not any(est.get('id') == id for est in estimates)

def calculate_expiry_date(estimate_date: str, expiry_terms: str = 'net_30') -> str:
    """Calculate expiry date based on estimate date and expiry terms"""
    try:
        date = datetime.strptime(estimate_date, '%Y-%m-%d')
        
        if expiry_terms == 'due_on_receipt':
            return estimate_date
        elif expiry_terms == 'net_15':
            date = date + timedelta(days=15)
        elif expiry_terms == 'net_30':
            date = date + timedelta(days=30)
        elif expiry_terms == 'net_60':
            date = date + timedelta(days=60)
        elif expiry_terms == 'custom':
            return estimate_date
        
        return date.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error calculating expiry date: {str(e)}")
        return (datetime.strptime(estimate_date, '%Y-%m-%d') + 
                timedelta(days=30)).strftime('%Y-%m-%d')

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
            
    except Exception as e:
        print(f"Error validating account ID: {str(e)}")
        return SALES_REVENUE_ID if account_type == 'income' else ACCOUNTS_RECEIVABLE_ID

# Interface Routes
@estimates_bp.route('/status_types', methods=['GET'])
def get_status_types():
    """Get all valid estimate status types"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(ESTIMATE_STATUSES)

@estimates_bp.route('/next_number', methods=['GET'])
def get_next_number():
    """Get the next available estimate number"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'estimate_no': get_next_estimate_number()})

# Operations Routes
@estimates_bp.route('/create_estimate', methods=['POST'])
def create_estimate():
    """Create a new estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        # Generate estimate ID and number
        estimate_id = generate_estimate_id()
        estimate_no = get_next_estimate_number()

        line_items = [LineItem(
            product_id=item['product_id'],
            description=item['description'],
            unit_price=float(item['unit_price']),
            quantity=float(item['quantity'])
        ) for item in data['line_items']]

        # Calculate totals
        total = sum(item.unit_price * item.quantity for item in line_items)
        
        # Set dates
        current_time = datetime.utcnow().isoformat()
        estimate_date = data.get('date', '').split('T')[0] if 'T' in data.get('date', '') else data.get('date')
        payment_terms = data.get('payment_terms', 'net_30')  # Changed default to match invoice default
        expiry_date = data.get('expiry_date', '').split('T')[0] if 'T' in data.get('expiry_date', '') else data.get('expiry_date')

        # Create estimate instance
        estimate = Estimate(
            id=estimate_id,
            estimate_no=estimate_no,
            estimate_date=estimate_date,
            expiry_date=expiry_date,
            customer_name=data['customer_name'],
            status='draft',
            line_items=line_items,
            total=total,
            payment_terms=payment_terms,
            customer_id=data.get('customer_id'),
            notes=data.get('notes'),
            created_at=current_time,
            updated_at=current_time
        )
        
        # Save estimate
        estimate.save(uid)
            
        return jsonify(estimate.to_dict()), 201
        
    except Exception as e:
        print(f"Error in create_estimate: {str(e)}")
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/update_estimate/<id>', methods=['PUT'])
def update_estimate(id):
    """Update an estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        # Load all estimates
        estimates_data = load_estimates(uid)
        
        # Get the estimates list from the data structure
        if isinstance(estimates_data, dict) and 'estimates' in estimates_data:
            estimates = estimates_data['estimates']
        else:
            return jsonify({'error': 'Invalid estimates data structure'}), 500
        
        # Find the estimate to update
        estimate_index = None
        for i, est in enumerate(estimates):
            if est['id'] == id:
                estimate_index = i
                break
                
        if estimate_index is None:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # Get current estimate
        current_estimate = estimates[estimate_index]
        
        # Validate status
        # if current_estimate['status'] not in ['draft', 'pending']:
        #     return jsonify({'error': 'Cannot update an accepted, declined, expired, converted estimate'}), 400
        
        current = Estimate.from_dict(current_estimate)

        allowed_fields = {
            'estimate_date', 'expiry_date', 'customer_name', 'status', 
            'line_items', 'payment_terms', 'customer_id', 'notes'
        }
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        # Special handling for line_items
        if 'line_items' in update_data:
            update_data['line_items'] = [
                LineItem(
                    product_id=item['product_id'],
                    description=item.get('description'),
                    unit_price=float(item['unit_price']),
                    quantity=float(item['quantity'])
                ) for item in update_data['line_items']
            ]
        
        # Update the estimate
        for key, value in update_data.items():
            setattr(current, key, value)
        
        # Update timestamps
        current.updated_at = datetime.utcnow().isoformat()
        
        # If status is being updated, set the appropriate timestamp
        if 'status' in update_data:
            if update_data['status'] == 'accepted':
                current.accepted_at = datetime.utcnow().isoformat()
            elif update_data['status'] == 'declined':
                current.declined_at = datetime.utcnow().isoformat()
            elif update_data['status'] == 'converted':
                current.converted_at = datetime.utcnow().isoformat()
        
        # Convert to dict using the model's method (which removes invoice-specific fields)
        updated_estimate = current.to_dict()
        
        # Update the estimate in the list
        estimates[estimate_index] = updated_estimate
        
        # Save all estimates
        estimates_data['estimates'] = estimates
        save_estimates(uid, estimates_data)
        
        return jsonify(updated_estimate), 200
        
    except Exception as e:
        print(f"Error in update_estimate: {str(e)}")
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/get_estimate/<id>', methods=['GET'])
def get_estimate(id):
    """Get estimate by ID"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
        return jsonify(estimate.to_dict())
    except Exception as e:
        print(f"Error in get_estimate: {str(e)}")
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/list_estimates', methods=['GET'])
def list_estimates():
    """Get all estimates with optional filters"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        estimates = Estimate.get_all(uid)
        
        # Apply filters if provided
        status = request.args.get('status')
        if status:
            estimates = [est for est in estimates if est.status == status]
            
        customer = request.args.get('customer')
        if customer:
            estimates = [est for est in estimates if customer.lower() in est.customer_name.lower()]
            
        # Convert to dict for response
        estimates_dict = [est.to_dict() for est in estimates]
        
        return jsonify({'estimates': estimates_dict})
    except Exception as e:
        print(f"Error in list_estimates: {str(e)}")
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/delete_estimate/<id>', methods=['DELETE'])
def delete_estimate(id):
    """Delete an estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # if estimate.status not in ['draft', 'declined', 'expired']:
        #     return jsonify({'error': 'Only draft, declined, or expired estimates can be deleted'}), 400
            
        # Delete estimate
        estimate.delete(uid)
        
        return jsonify({'message': 'Estimate deleted successfully'})
    except Exception as e:
        print(f"Error in delete_estimate: {str(e)}")
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/expire_estimate/<id>', methods=['POST'])
def expire_estimate(id):
    """Expire an estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:

        
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # if estimate.status not in ['draft', 'sent']:
        #     return jsonify({'error': 'Only draft or sent estimates can be expired'}), 400
            
        estimate.status = 'expired'
        estimate.expired_at = datetime.utcnow().isoformat() 
        estimate.save(uid)
        
        return jsonify(estimate.to_dict()), 200
    except Exception as e:
        print(f"Error in expire_estimate: {str(e)}")
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

@estimates_bp.route('/send/<id>', methods=['POST'])
def send_estimate(id):
    """Mark estimate as sent to customer"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # if estimate.status not in ['draft']:
        #     return jsonify({'error': 'Only draft estimates can be sent'}), 400
            
        # Update estimate
        estimate.status = 'pending'
        estimate.sent_at = datetime.utcnow().isoformat()
        estimate.save(uid)
        return jsonify(estimate.to_dict()), 200

    except Exception as e:
        print(f"Error in send_estimate: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@estimates_bp.route('/accept_estimate/<id>', methods=['POST'])
def accept_estimate(id):
    """Accept an estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # if estimate.status != 'pending':
        #     return jsonify({'error': 'Only pending estimates can be accepted'}), 400
            
        estimate.status = 'accepted'
        estimate.accepted_at = datetime.utcnow().isoformat()
        estimate.save(uid)
        
        return jsonify(estimate.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/decline_estimate/<id>', methods=['POST'])
def decline_estimate(id):
    """Decline an estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # if estimate.status != 'pending':
        #     return jsonify({'error': 'Only pending estimates can be declined'}), 400
            
        estimate.status = 'declined'
        estimate.declined_at = datetime.utcnow().isoformat()
        estimate.decline_reason = data.get('reason')
        estimate.save(uid)
        
        return jsonify(estimate.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/convert_to_invoice/<id>', methods=['POST'])
def convert_to_invoice(id):
    """Convert an estimate to an invoice"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load estimate
        estimate = Estimate.get_by_id(uid, id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # if estimate.status not in ['accepted', 'pending']:
        #     return jsonify({'error': 'Only accepted or pending estimates can be converted'}), 400
        
        current_time = datetime.utcnow().isoformat()
        base_data = {
            # BaseDocument required fields
            'id': Invoice.generate_invoice_id(),
            'customer_id': estimate.customer_id,
            'date': current_time,
            'payment_terms': estimate.payment_terms,
            'status': 'draft',
            'line_items': estimate.line_items,
            'total': estimate.total,
            'notes': estimate.notes,
            'created_at': current_time,
            'updated_at': current_time,
            
            # Invoice specific fields
            'invoice_no': f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000,9999)}",
            'invoice_date': current_time,
            'due_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'customer_name': estimate.customer_name,
            'balance_due': estimate.total,
            'payments': [],
            'sent_at': None,
            'voided_at': None,
            'void_reason': None,
            'last_payment_date': None,
            'converted_from_estimate': estimate.to_dict()
        }

        # Create invoice with all data at once
        invoice = Invoice(**base_data)
        invoice.save(uid)
                
        # Update estimate
        estimate.status = 'converted'
        estimate.converted_at = datetime.utcnow().isoformat()
        estimate.converted_to_invoice = invoice.to_dict()
        estimate.save(uid)
        
        return jsonify(estimate.to_dict()), 200
        
    except Exception as e:
        print(f"Error converting estimate: {str(e)}")
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/duplicate/<id>', methods=['POST'])
def duplicate_estimate(id):
    """Create a copy of an existing estimate"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load original estimate
        original = Estimate.get_by_id(uid, id)
        if not original:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # Create new estimate data
        new_estimate_data = original.to_dict()
        
        # Update fields for new estimate
        new_estimate_data.update({
            'id': generate_estimate_id(),
            'estimate_no': get_next_estimate_number(),
            'estimate_date': datetime.utcnow().isoformat(),
            'due_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),  # Default 30 days
            'status': 'draft',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Remove fields that shouldn't be copied
        fields_to_remove = [
            'sent_at', 
            'accepted_at', 
            'declined_at', 
            'converted_at',
            'accepted_by',
            'declined_by',
            'decline_reason',
            'converted_to_invoice'
        ]
        for field in fields_to_remove:
            new_estimate_data.pop(field, None)
            
        # Create and save new invoice
        new_estimate = Estimate.from_dict(new_estimate_data)
        new_estimate.save(uid)
        
        return jsonify(new_estimate.to_dict()), 201
        
    except Exception as e:
        print(f"Error in duplicate_estimate: {str(e)}")
        return jsonify({'error': str(e)}), 500

@estimates_bp.route('/update_summary', methods=['POST'])
def update_summary_route():
    """Update estimates summary"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = load_estimates(uid)
        if not data or 'estimates' not in data:
            return jsonify({'error': 'No estimates data found'}), 404
            
        summary = update_summary(data['estimates'])
        data['summary'] = summary.to_dict()
        save_estimates(uid, data)
        return jsonify(summary.to_dict()), 200
    except Exception as e:
        print(f"Error in update_summary_route: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 400

@estimates_bp.route('/get_summary', methods=['GET'])
def get_summary():
    """Get estimates summary"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = load_estimates(uid)
        if not data or 'estimates' not in data:
            return jsonify({'error': 'No estimates data found'}), 404
            
        summary = update_summary(data['estimates'])
        return jsonify(summary.to_dict()), 200
    except Exception as e:
        print(f"Error in get_summary: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 400