from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import random

from . import estimates_bp
from .models import Estimate, EstimatesSummary, Product, ESTIMATE_STATUSES
from app.invoices.routes import (
    load_invoices, save_invoices, get_next_invoice_number,
    generate_invoice_id, update_summary as update_invoice_summary,
    validate_account_id
)
from app.chart_of_accounts.routes import load_chart_of_accounts
from app.products.routes import load_products
from app.transactions.models import Transaction, TransactionType, TransactionSubType, TransactionEntry
from app.transactions.routes import create_transaction_direct, load_transactions, save_transactions

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ESTIMATES_FILE = os.path.join(DATA_DIR, 'estimates.json')

# Default account IDs - these should match your chart of accounts
def get_system_accounts():
    """Get account IDs from chart of accounts"""
    accounts = load_chart_of_accounts().get('accounts', [])
    ar_account = next((acc for acc in accounts if acc['accountType'] == 'Accounts Receivable' and acc['isDefault']), None)
    ap_account = next((acc for acc in accounts if acc['accountType'] == 'Accounts Payable' and acc['isDefault']), None)
    sales_account = next((acc for acc in accounts if acc['accountType'] == 'Income' and acc['isDefault']), None)
    cogs_account = next((acc for acc in accounts if acc['accountType'] == 'Cost of Goods Sold' and acc['isDefault']), None)
    inventory_account = next((acc for acc in accounts if acc['accountType'] == 'Other Current Asset' and acc['detailType'] == 'Inventory' and acc['isDefault']), None)
    
    if not all([ar_account, ap_account, sales_account, cogs_account, inventory_account]):
        raise Exception("Required system accounts not found in chart of accounts")
        
    return {
        'ACCOUNTS_RECEIVABLE_ID': ar_account['id'],
        'ACCOUNTS_PAYABLE_ID': ap_account['id'],
        'SALES_REVENUE_ID': sales_account['id'],
        'COGS_ID': cogs_account['id'],
        'INVENTORY_ASSET_ID': inventory_account['id']
    }

# Initialize system accounts
try:
    system_accounts = get_system_accounts()
    ACCOUNTS_RECEIVABLE_ID = system_accounts['ACCOUNTS_RECEIVABLE_ID']
    ACCOUNTS_PAYABLE_ID = system_accounts['ACCOUNTS_PAYABLE_ID']
    SALES_REVENUE_ID = system_accounts['SALES_REVENUE_ID']
    COGS_ID = system_accounts['COGS_ID']
    INVENTORY_ASSET_ID = system_accounts['INVENTORY_ASSET_ID']
except Exception as e:
    print(f"Error loading system accounts: {str(e)}")
    # Fallback values in case of error - these should match your chart of accounts
    ACCOUNTS_RECEIVABLE_ID = "1100-0001"  # Accounts Receivable
    ACCOUNTS_PAYABLE_ID = "2100-0001"     # Accounts Payable
    SALES_REVENUE_ID = "4000-0001"        # Sales Revenue
    COGS_ID = "5000-0001"                 # Cost of Goods Sold
    INVENTORY_ASSET_ID = "1200-0001"      # Inventory Asset

def deep_update(original: Dict, update: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def load_estimates() -> Dict:
    """Load estimates data from JSON file"""
    try:
        if os.path.exists(ESTIMATES_FILE):
            with open(ESTIMATES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading estimates data: {str(e)}")
    return {'estimates': [], 'summary': {}}

def save_estimates(data: Dict) -> bool:
    """Save estimates data to JSON file"""
    try:
        with open(ESTIMATES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving estimates data: {str(e)}")
        return False

def update_summary(estimates: List[Dict]) -> EstimatesSummary:
    """Update estimates summary information"""
    summary = EstimatesSummary()
    summary.total_count = len(estimates)
    summary.total_amount = sum(float(est.get('total_amount', 0)) for est in estimates)
    return summary

def get_next_estimate_number() -> str:
    """Generate the next estimate number"""
    data = load_estimates()
    estimates = data.get('estimates', [])
    if not estimates:
        return "EST-2024-001"
    
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

def get_preferred_payment_terms():
    """Get default payment terms"""
    return "due_on_receipt"

def calculate_due_date(invoice_date, payment_terms):
    """Calculate due date based on payment terms"""
    return invoice_date  # For now, just return same date for due_on_receipt

def create_estimate_transaction(estimate_data: Dict, sub_type: str = 'estimate_draft') -> None:
    """Create a transaction record for an estimate"""
    try:
        # Calculate total amount
        total_amount = sum(float(product['price']) * float(product['quantity']) 
                         for product in estimate_data.get('products', []))

        # Create transaction
        transaction_data = {
            'date': estimate_data['estimate_date'],
            'description': f"Estimate {estimate_data['estimate_no']} created",
            'transaction_type': TransactionType.ESTIMATE.value,
            'sub_type': sub_type,
            'reference_type': 'estimate',
            'reference_id': estimate_data['id'],
            'status': 'draft',
            'customer_name': estimate_data['customer_name'],
            'products': estimate_data['products'],
            'entries': [],  # No accounting entries for estimates as they don't affect the books
            'amount': total_amount
        }
        
        create_transaction_direct(transaction_data)
        
    except Exception as e:
        print(f"Error creating estimate transaction: {str(e)}")
        raise

def update_estimate_transaction(estimate_data: Dict, sub_type: str) -> None:
    """Update the transaction record for an estimate"""
    try:
        # Load transactions
        transactions_data = load_transactions()
        transactions = transactions_data.get('transactions', [])
        
        # Find the estimate's transaction
        transaction_index = None
        for i, txn in enumerate(transactions):
            if (txn.get('reference_type') == 'estimate' and 
                txn.get('reference_id') == estimate_data['id']):
                transaction_index = i
                break
        
        if transaction_index is not None:
            # Update transaction
            transaction = transactions[transaction_index]
            transaction['sub_type'] = sub_type
            transaction['description'] = f"Estimate {estimate_data['estimate_no']} updated"
            transaction['amount'] = sum(float(product['price']) * float(product['quantity']) 
                                     for product in estimate_data.get('products', []))
            transaction['products'] = estimate_data['products']
            transaction['updated_at'] = datetime.utcnow().isoformat()
            
            # Save changes
            save_transactions(transactions_data)
            
    except Exception as e:
        print(f"Error updating estimate transaction: {str(e)}")
        raise

def delete_estimate_transaction(estimate_id: str) -> None:
    """Delete the transaction record for an estimate"""
    try:
        # Load transactions
        transactions_data = load_transactions()
        transactions = transactions_data.get('transactions', [])
        
        # Find and remove the estimate's transaction
        transaction_index = None
        for i, txn in enumerate(transactions):
            if (txn.get('reference_type') == 'estimate' and 
                txn.get('reference_id') == estimate_id):
                transaction_index = i
                break
        
        if transaction_index is not None:
            transactions.pop(transaction_index)
            save_transactions(transactions_data)
            
    except Exception as e:
        print(f"Error deleting estimate transaction: {str(e)}")
        raise

# Interface Routes
@estimates_bp.route('/status_types', methods=['GET'])
def get_status_types():
    """Get all valid estimate status types"""
    return jsonify(ESTIMATE_STATUSES)

@estimates_bp.route('/next_number', methods=['GET'])
def get_next_number():
    """Get the next available estimate number"""
    return jsonify({'estimate_no': get_next_estimate_number()})

# Operations Routes
@estimates_bp.route('/create_estimate', methods=['POST'])
def create_estimate():
    """Create a new estimate"""
    try:
        data = request.get_json()
        
        # Load products data
        products_data = load_products()
        products_map = {p['id']: p for p in products_data.get('products', [])}
        
        # Generate estimate ID and number
        estimate_id = generate_estimate_id()
        while not is_id_unique(estimate_id, load_estimates().get('estimates', [])):
            estimate_id = generate_estimate_id()
            
        data['id'] = estimate_id
        data['estimate_no'] = get_next_estimate_number()
        
        # Set dates
        data['estimate_date'] = data.get('estimate_date', datetime.utcnow().date().isoformat())
        data['expiry_date'] = data.get('expiry_date') or calculate_due_date(data.get('estimate_date'), 'net_30')
        data['created_at'] = datetime.utcnow().date().isoformat()
        data['updated_at'] = data['created_at']
        data['status'] = data.get('status', 'draft')
        
        # Process products with full product info
        processed_products = []
        for product in data.get('products', []):
            # Get full product info if ID exists
            product_info = products_map.get(product.get('id'))
            
            if product_info:
                # Use existing product info
                estimate_product = {
                    'id': product_info['id'],
                    'name': product_info['name'],
                    'description': product_info.get('description', ''),  
                    'price': float(product.get('price', product_info['unit_price'])),
                    'cost_price': float(product_info.get('cost_price', product_info.get('cost_price', 0))),
                    'quantity': float(product.get('quantity', 1)),
                    'type': product_info['type'],
                    'sell_enabled': product_info['sell_enabled'],
                    'purchase_enabled': product_info['purchase_enabled'],
                    'income_account_id': product_info.get('income_account_id'),
                    'expense_account_id': product_info.get('expense_account_id')
                }
                
                # Add inventory info if present
                if 'inventory_info' in product_info:
                    estimate_product['inventory_info'] = product_info['inventory_info']
            else:
                # Handle product without ID (new product)
                product_type = product.get('type', 'service')
                estimate_product = {
                    'id': product.get('id', ''),
                    'name': product['name'],
                    'description': product.get('description', ''),
                    'price': float(product.get('price', 0)),
                    'cost_price': float(product.get('cost_price', 0)),
                    'quantity': float(product.get('quantity', 1)),
                    'type': product_type,
                    'sell_enabled': product.get('sell_enabled', True),
                    'purchase_enabled': product.get('purchase_enabled', False),
                    'income_account_id': product.get('income_account_id', SALES_REVENUE_ID),
                    'expense_account_id': COGS_ID if product_type == 'inventory_item' else None
                }
                
            processed_products.append(estimate_product)
            
        data['products'] = processed_products
        
        # Create estimate object and validate
        estimate = Estimate.from_dict(data)
        
        # Save estimate
        estimates_data = load_estimates()
        estimates_data['estimates'].append(estimate.to_dict())
        
        # Update summary
        estimates_data['summary'] = update_summary(estimates_data['estimates']).to_dict()
        
        create_estimate_transaction(data)
        
        if not save_estimates(estimates_data):
            return jsonify({'message': 'Failed to save estimate'}), 500
            
        return jsonify(estimate.to_dict()), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating estimate: {str(e)}'}), 500

@estimates_bp.route('/update_estimate/<string:id>', methods=['PATCH'])
def update_estimate(id):
    """Update an estimate"""
    try:
        data = request.get_json()
        
        # Load estimate
        estimates_data = load_estimates()
        estimate_index = None
        estimate = None
        
        for i, est in enumerate(estimates_data['estimates']):
            if est['id'] == id:
                estimate_index = i
                estimate = est
                break
                
        if estimate is None:
            return jsonify({'message': 'Estimate not found'}), 404
            
        # Validate product account IDs in update data
        if 'products' in data:
            for product in data['products']:
                # Validate income account ID
                product['income_account_id'] = validate_account_id(
                    product.get('income_account_id', SALES_REVENUE_ID),
                    'income'
                )
                
                # If it's an inventory item, validate expense account ID
                if product.get('type') == 'inventory_item':
                    product['expense_account_id'] = validate_account_id(
                        product.get('expense_account_id', COGS_ID),
                        'expense'
                    )
        
        # Update estimate
        data['updated_at'] = datetime.utcnow().date().isoformat()
        deep_update(estimate, data)
        
        # Validate updated estimate
        updated_estimate = Estimate.from_dict(estimate)
        estimates_data['estimates'][estimate_index] = updated_estimate.to_dict()
        
        # Update summary
        estimates_data['summary'] = update_summary(estimates_data['estimates']).to_dict()
        
        # Pass the full estimate data to update_estimate_transaction
        update_estimate_transaction(updated_estimate.to_dict(), data.get('status', 'estimate_updated'))
        
        if not save_estimates(estimates_data):
            return jsonify({'message': 'Failed to save estimate'}), 500
            
        return jsonify(updated_estimate.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error updating estimate: {str(e)}'}), 500

@estimates_bp.route('/list_estimates', methods=['GET'])
def list_estimates():
    """Get all estimates with optional filters"""
    try:
        # Load data
        data = load_estimates()
        estimates = data.get('estimates', [])
        
        # Apply filters
        status = request.args.get('status')
        search = request.args.get('search', '').lower()
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        filtered_estimates = estimates
        
        if status and status != 'All':
            filtered_estimates = [est for est in filtered_estimates if est['status'] == status]
            
        if search:
            filtered_estimates = [
                est for est in filtered_estimates
                if search in est['customer_name'].lower() or
                   search in est['estimate_no'].lower()
            ]
            
        if date_from:
            filtered_estimates = [
                est for est in filtered_estimates
                if est['estimate_date'] >= date_from
            ]
            
        if date_to:
            filtered_estimates = [
                est for est in filtered_estimates
                if est['estimate_date'] <= date_to
            ]
        
        # Update summary for filtered results
        summary = update_summary(filtered_estimates)
        
        return jsonify({
            'estimates': filtered_estimates,
            'summary': summary.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/get_estimate/<id>', methods=['GET'])
def get_estimate(id):
    """Get estimate by ID"""
    try:
        data = load_estimates()
        estimates = data.get('estimates', [])
        
        estimate = next((est for est in estimates if est['id'] == id), None)
        if estimate:
            return jsonify(estimate)
        else:
            return jsonify({'error': 'Estimate not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/delete_estimate/<id>', methods=['DELETE'])
def delete_estimate(id):
    """Delete an estimate"""
    try:
        # Load current data
        data_store = load_estimates()
        estimates = data_store.get('estimates', [])
        
        # Find estimate
        estimate_index = next((i for i, est in enumerate(estimates) if est['id'] == id), None)
        if estimate_index is None:
            return jsonify({'error': 'Estimate not found'}), 404

        # Remove estimate
        estimates.pop(estimate_index)
        data_store['estimates'] = estimates
        data_store['summary'] = update_summary(estimates).to_dict()
        
        delete_estimate_transaction(id)
        
        if save_estimates(data_store):
            return '', 204
        else:
            return jsonify({'error': 'Failed to save changes'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/convert_to_invoice/<string:id>', methods=['POST'])
def convert_to_invoice(id):
    """Convert an estimate to an invoice"""
    try:
        # Load estimate
        estimates_data = load_estimates()
        estimate = next((est for est in estimates_data['estimates'] if est['id'] == id), None)
        
        if estimate is None:
            return jsonify({'message': 'Estimate not found'}), 404
            
        if estimate.get('status') == 'converted':
            return jsonify({'message': 'Estimate already converted to invoice'}), 400
            
        # Create invoice data
        invoice_data = {
            'customer_name': estimate['customer_name'],
            'customer_id': estimate.get('customer_id'),
            'products': [
                {
                    'id': product.get('id', ''),
                    'name': product['name'],
                    'description': product.get('description', ''),
                    'price': float(product['price']),
                    'cost_price': float(product.get('cost_price', 0)),
                    'quantity': float(product['quantity']),
                    'type': product.get('type', ''),
                    'sell_enabled': product.get('sell_enabled', True),
                    'purchase_enabled': product.get('purchase_enabled', False),
                    'income_account_id': product.get('income_account_id'),
                    'expense_account_id': product.get('expense_account_id')
                }
                for product in estimate['products']
            ],
            'payment_terms': estimate.get('payment_terms', 'due_on_receipt'),
            'status': 'draft',
            'payments': [],
            'last_payment_date': None
        }
        
        # Calculate total amount
        total_amount = sum(
            float(product['price']) * float(product['quantity'])
            for product in invoice_data['products']
        )
        invoice_data['total_amount'] = total_amount
        invoice_data['balance_due'] = total_amount
        
        # Set dates
        invoice_date = datetime.utcnow().date().isoformat()
        invoice_data['invoice_date'] = invoice_date
        invoice_data['due_date'] = calculate_due_date(invoice_date, invoice_data['payment_terms'])
        
        # Load invoices
        invoices_data = load_invoices()
        
        # Generate invoice ID and number
        invoice_data['id'] = generate_invoice_id()
        while any(inv.get('id') == invoice_data['id'] for inv in invoices_data.get('invoices', [])):
            invoice_data['id'] = generate_invoice_id()
            
        invoice_data['invoice_no'] = get_next_invoice_number()
        invoice_data['created_at'] = invoice_date
        invoice_data['updated_at'] = invoice_date
        
        # Add conversion info
        invoice_data['converted_from_estimate'] = {
            'id': estimate['id'],
            'estimate_no': estimate['estimate_no'],
            'conversion_date': invoice_date
        }
        
        # Update estimate status and add conversion info
        estimate['status'] = 'converted'
        estimate['updated_at'] = invoice_date
        estimate['conversion_info'] = {
            'invoice_id': invoice_data['id'],
            'invoice_no': invoice_data['invoice_no'],
            'conversion_date': invoice_date
        }
        
        # Update estimate transaction to mark as converted
        update_estimate_transaction(estimate, 'estimate_converted')
        
        # Save estimate changes
        if not save_estimates(estimates_data):
            return jsonify({'message': 'Failed to update estimate status'}), 500
            
        # Create invoice
        invoices_data['invoices'].append(invoice_data)
        
        # Update invoice summary
        invoices_data['summary'] = update_invoice_summary(invoices_data['invoices']).to_dict()
        
        if not save_invoices(invoices_data):
            return jsonify({'message': 'Failed to create invoice'}), 500
            
        # Delete estimate transaction since it's now converted
        delete_estimate_transaction(estimate['id'])
        
        # Create transaction for the new invoice
        products = invoice_data['products']
        entries = []
        total_amount = sum(float(p.get('price', 0)) * float(p.get('quantity', 0)) for p in products)
        total_cost = 0
        
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
        for product in products:
            if product.get('type') == 'inventory_item':
                # Calculate cost amount
                cost_price = float(product.get('cost_price', 0))
                quantity = float(product.get('quantity', 0))
                cost_amount = cost_price * quantity
                total_cost += cost_amount
        
        # Only add COGS entries if there are inventory items
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
        
        transaction_data = {
            'date': invoice_data['invoice_date'],
            'description': f"Invoice {invoice_data['invoice_no']} created from estimate {estimate['estimate_no']}",
            'transaction_type': TransactionType.INVOICE.value,
            'sub_type': 'invoice_draft',
            'reference_type': 'invoice',
            'reference_id': invoice_data['id'],
            'status': 'draft',
            'customer_name': invoice_data['customer_name'],
            'products': invoice_data['products'],
            'entries': entries,
            'amount': total_amount
        }
        create_transaction_direct(transaction_data)
            
        return jsonify({
            'message': 'Estimate converted to invoice successfully',
            'invoice': invoice_data
        })
        
    except Exception as e:
        return jsonify({'message': f'Error converting estimate to invoice: {str(e)}'}), 500
