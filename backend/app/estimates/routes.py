from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import random
import sys

from . import estimates_bp
from .models import Estimate, EstimatesSummary, Product, ESTIMATE_STATUSES

# Add path to allow importing from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from invoices.routes import (
    load_invoices, save_invoices, get_next_invoice_number,
    generate_invoice_id, update_summary as update_invoice_summary
)

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ESTIMATES_FILE = os.path.join(DATA_DIR, 'estimates.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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
        
        # Validate required fields
        required_fields = ['customer_name', 'estimate_date', 'products', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate products
        if not isinstance(data['products'], list):
            return jsonify({'error': 'Products must be a list'}), 400
        
        for product in data['products']:
            if not all(key in product for key in ['name', 'description', 'price']):
                return jsonify({'error': 'Each product must have name, description, and price'}), 400

        # Generate unique ID
        data_store = load_estimates()
        estimates = data_store.get('estimates', [])
        
        while True:
            new_id = generate_estimate_id()
            if is_id_unique(new_id, estimates):
                break

        # Set estimate number
        data['estimate_no'] = get_next_estimate_number()
        data['id'] = new_id

        # Create estimate instance
        estimate = Estimate.from_dict(data)
        
        # Add to storage
        estimates.append(estimate.to_dict())
        data_store['estimates'] = estimates
        data_store['summary'] = update_summary(estimates).to_dict()
        
        if save_estimates(data_store):
            return jsonify(estimate.to_dict()), 201
        else:
            return jsonify({'error': 'Failed to save estimate'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

@estimates_bp.route('/update_estimate/<id>', methods=['PATCH'])
def update_estimate(id):
    """Update an estimate"""
    try:
        update_data = request.get_json()
        
        # Validate products if provided
        if 'products' in update_data:
            if not isinstance(update_data['products'], list):
                return jsonify({'error': 'Products must be a list'}), 400
            
            for product in update_data['products']:
                if not all(key in product for key in ['name', 'description', 'price']):
                    return jsonify({'error': 'Each product must have name, description, and price'}), 400

        # Load current data
        data_store = load_estimates()
        estimates = data_store.get('estimates', [])
        
        # Find and update estimate
        estimate_index = next((i for i, est in enumerate(estimates) if est['id'] == id), None)
        if estimate_index is None:
            return jsonify({'error': 'Estimate not found'}), 404

        # Check if estimate is already accepted
        if estimates[estimate_index]['status'] == 'accepted':
            return jsonify({'error': 'Cannot edit an accepted estimate'}), 400

        # Create updated estimate
        current_estimate = estimates[estimate_index]
        
        # If products are being updated, replace the entire products list
        if 'products' in update_data:
            current_estimate['products'] = update_data['products']
            # Remove products key from update_data to prevent double update
            del update_data['products']
            
        # Update other fields
        current_estimate.update(update_data)
        
        # Calculate total amount
        current_estimate['total_amount'] = sum(float(product.get('price', 0)) for product in current_estimate['products'])
        
        # Update timestamp
        current_estimate['updated_at'] = datetime.utcnow().isoformat()
        
        # Create estimate object and validate
        updated_estimate = Estimate.from_dict(current_estimate)
        
        # Save changes
        estimates[estimate_index] = updated_estimate.to_dict()
        data_store['estimates'] = estimates
        data_store['summary'] = update_summary(estimates).to_dict()
        
        if save_estimates(data_store):
            return jsonify(updated_estimate.to_dict())
        else:
            return jsonify({'error': 'Failed to save changes'}), 500

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
        
        if save_estimates(data_store):
            return '', 204
        else:
            return jsonify({'error': 'Failed to save changes'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@estimates_bp.route('/convert_to_invoice/<id>', methods=['POST'])
def convert_to_invoice(id):
    """Convert an estimate to an invoice"""
    try:
        # Load estimates
        estimates_data = load_estimates()
        estimate = next((est for est in estimates_data['estimates'] if est['id'] == id), None)
        
        if not estimate:
            return jsonify({"error": "Estimate not found"}), 404
            
        # Check if estimate can be converted
        if estimate.get('converted_to_invoice'):
            return jsonify({"error": "Estimate already converted to invoice"}), 400
            
        # For now, allow any status to be converted
        # if estimate['status'] not in ['accepted', 'sent']:
        #     return jsonify({"error": "Only accepted or sent estimates can be converted to invoices"}), 400
            
        # Get payment terms from request or use preferred terms
        try:
            data = request.get_json() or {}
        except Exception:
            data = {}
            
        payment_terms = data.get('payment_terms', get_preferred_payment_terms())
        invoice_date = datetime.now().strftime("%Y-%m-%d")
            
        # Create new invoice
        new_invoice = {
            "id": generate_invoice_id(),
            "invoice_no": get_next_invoice_number(),
            "invoice_date": invoice_date,
            "due_date": calculate_due_date(invoice_date, payment_terms),
            "customer_name": estimate['customer_name'],
            "status": "draft",
            "products": estimate['products'],
            "total_amount": float(estimate['total_amount']),
            "balance_due": float(estimate['total_amount']),
            "payments": [],
            "payment_terms": payment_terms,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "converted_from_estimate": {
                "id": estimate['id'],
                "estimate_no": estimate['estimate_no'],
                "conversion_date": datetime.now().isoformat()
            }
        }
        
        # Update estimate with conversion info and status
        estimate['converted_to_invoice'] = {
            "id": new_invoice['id'],
            "invoice_no": new_invoice['invoice_no'],
            "conversion_date": datetime.now().isoformat()
        }
        estimate['status'] = 'accepted'
        estimate['updated_at'] = datetime.now().isoformat()
        
        # Save estimate changes
        save_estimates(estimates_data)
        
        # Add invoice to invoices.json
        invoices_data = load_invoices()
        invoices = invoices_data.get('invoices', [])
        invoices.append(new_invoice)
        invoices_data['invoices'] = invoices
        invoices_data['summary'] = update_invoice_summary(invoices).to_dict()
        save_invoices(invoices_data)
        
        return jsonify({
            "message": "Estimate converted to invoice successfully",
            "invoice": new_invoice
        }), 200
        
    except Exception as e:
        print(f"Error converting estimate to invoice: {str(e)}")
        return jsonify({"error": "Failed to convert estimate"}), 500
