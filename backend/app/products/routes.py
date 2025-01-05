from flask import jsonify, request, Blueprint
import json
import os
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import random
import sys

from . import products_bp
from .models import Product, ProductsSummary, ITEM_TYPES
from app.chart_of_accounts.routes import load_chart_of_accounts

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')

# Default account IDs - these should match your chart of accounts
SALES_REVENUE_ID = "4000-0001"     # Sales Revenue
COGS_ID = "5000-0001"              # Cost of Goods Sold
INVENTORY_ASSET_ID = "1200-0001"   # Inventory Asset

def deep_update(original: Dict, update: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def load_products() -> Dict:
    """Load products data from JSON file"""
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading products data: {str(e)}")
    return {'products': [], 'summary': {}}

def save_products(data: Dict) -> bool:
    """Save products data to JSON file"""
    try:
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving products data: {str(e)}")
        return False

def update_summary(products: List[Dict]) -> ProductsSummary:
    """Update products summary information"""
    summary = ProductsSummary()
    summary.total_count = len(products)
    summary.service_count = sum(1 for p in products if p.get('type') == 'service')
    summary.inventory_count = sum(1 for p in products if p.get('type') == 'inventory_item')
    return summary

def generate_product_id() -> str:
    """Generate a random 8-digit ID with a dash in the middle"""
    first_half = str(random.randint(1000, 9999))
    second_half = str(random.randint(1000, 9999))
    return f"{first_half}-{second_half}"

def is_id_unique(id: str, products: List[Dict]) -> bool:
    """Check if an ID is unique among existing products"""
    return not any(prod.get('id') == id for prod in products)

def validate_product(data: Dict, for_update: bool = False) -> Optional[Dict]:
    """Validate product data"""
    if not for_update:
        required_fields = ['name', 'unit_price', 'type']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {'error': f'Missing required fields: {", ".join(missing_fields)}'}
    
    # Validate prices
    if 'unit_price' in data and float(data['unit_price']) < 0:
        return {'error': 'Unit price cannot be negative'}
        
    # Validate cost_price for inventory items
    if data.get('type') == 'inventory_item':
        if 'cost_price' not in data:
            return {'error': 'Cost price is required for inventory items'}
        if float(data['cost_price']) < 0:
            return {'error': 'Cost price cannot be negative'}
        if float(data['cost_price']) >= float(data['unit_price']):
            return {'error': 'Cost price must be lower than unit price'}
            
    return None

def validate_account_id(account_id: str, account_type: str) -> str:
    """Validate account ID and return default if invalid"""
    try:
        # Load accounts
        accounts_data = load_chart_of_accounts()
        accounts = accounts_data.get('accounts', [])
        
        # Find account by ID
        for account in accounts:
            if account['id'] != account_id:
                continue
                
            # Validate account type
            if account_type == 'income' and account['accountType'] in ['Income', 'Other Income']:
                return account['id']  # Always return the ID, not the name
            elif account_type == 'expense' and account['accountType'] in ['Expense', 'Cost of Sales']:
                return account['id']  # Always return the ID, not the name
            elif account_type == 'inventory' and account['detailType'] == 'Inventory':
                return account['id']  # Always return the ID, not the name
            elif account_type == 'Cost of Goods Sold' and account['accountType'] in ['Cost of Goods Sold']:
                return account['id']  # Always return the ID, not the name
                
        # Return default based on type
        if account_type == 'income':
            return SALES_REVENUE_ID
        elif account_type == 'expense':
            return COGS_ID
        elif account_type == 'inventory':
            return INVENTORY_ASSET_ID
        elif account_type == 'Cost of Goods Sold':
            return COGS_ID
            
    except Exception as e:
        print(f"Error validating account ID: {str(e)}")
        return SALES_REVENUE_ID if account_type == 'income' else COGS_ID if account_type in ['expense', 'Cost of Goods Sold'] else INVENTORY_ASSET_ID

# API Routes
@products_bp.route('/list', methods=['GET'])
def list_products():
    """List all products with optional filtering"""
    try:
        # Get query parameters
        type_filter = request.args.get('type')
        category = request.args.get('category')
        
        # Load data
        data = load_products()
        products = data.get('products', [])
        
        # Apply filters
        if type_filter:
            products = [p for p in products if p.get('type') == type_filter]
        if category:
            products = [p for p in products if p.get('category') == category]
            
        return jsonify({
            'products': products,
            'summary': update_summary(products).to_dict()
        })
        
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@products_bp.route('/get/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    try:
        data = load_products()
        product = next((p for p in data.get('products', []) if p.get('id') == product_id), None)
        
        if not product:
            return jsonify({"error": {"message": "Product not found"}}), 404
            
        return jsonify(product)
        
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@products_bp.route('/create', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # For inventory items, enforce purchase_enabled and sell_enabled
        if data.get('type') == 'inventory_item':
            data['purchase_enabled'] = True
            data['sell_enabled'] = True
            
            # Validate inventory asset account
            if 'inventory_info' in data:
                data['inventory_info']['inventory_asset_account_id'] = validate_account_id(
                    data['inventory_info'].get('inventory_asset_account_id', INVENTORY_ASSET_ID),
                    'inventory'
                )
                
            # Validate income/expense with specific types for inventory items
            data['income_account_id'] = validate_account_id(
                data.get('income_account_id', '4000-0001'),  # Default Sales Revenue ID
                'income'
            )
            data['expense_account_id'] = validate_account_id(
                data.get('expense_account_id', '5000-0001'),  # Default COGS ID
                'expense'
            )
        else:
            # For non-inventory items, validate with normal account types
            if data.get('sell_enabled', True):
                data['income_account_id'] = validate_account_id(
                    data.get('income_account_id', '4000-0001'),  # Default Sales Revenue ID
                    'income'
                )
            if data.get('purchase_enabled', False):
                data['expense_account_id'] = validate_account_id(
                    data.get('expense_account_id', '5000-0001'),  # Default COGS ID
                    'expense'
                )

        # Validate data
        errors = validate_product(data)
        if errors:
            return jsonify({"error": {"message": errors['error']}}), 400
        
        # Load existing data
        products_data = load_products()
        products = products_data.get('products', [])
        
        # Generate unique ID
        product_id = generate_product_id()
        while not is_id_unique(product_id, products):
            product_id = generate_product_id()
        
        # Create product with ID and handle SKU
        data['id'] = product_id
        # If SKU is not provided or is empty, use the product_id
        if not data.get('sku'):
            data['sku'] = product_id
        
        # Set timestamps
        now = datetime.utcnow().date().isoformat()
        data['created_at'] = now
        data['updated_at'] = now
        
        product = Product.from_dict(data)
        
        # Add to products list
        products.append(product.to_dict())
        
        # Update summary
        products_data['summary'] = update_summary(products).to_dict()
        products_data['products'] = products
        
        # Save to file
        if save_products(products_data):
            return jsonify(product.to_dict()), 201
        else:
            return jsonify({"error": {"message": "Failed to save product"}}), 500
            
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@products_bp.route('/update/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    try:
        data = request.get_json()
        
        # Load existing data
        products_data = load_products()
        products = products_data.get('products', [])
        
        # Find product
        product_index = next((i for i, p in enumerate(products) if p.get('id') == product_id), None)
        if product_index is None:
            return jsonify({"error": {"message": "Product not found"}}), 404
        
        # Create updated product
        current_product = products[product_index]
        updated_data = current_product.copy()
        
        # Validate account IDs in the update data
        if 'income_account_id' in data:
            data['income_account_id'] = validate_account_id(
                data['income_account_id'],
                'income'
            )
        
        if 'expense_account_id' in data:
            data['expense_account_id'] = validate_account_id(
                data['expense_account_id'],
                'expense'
            )
        
        if 'inventory_info' in data and data.get('type', current_product.get('type')) == 'inventory_item':
            if 'inventory_asset_account_id' in data['inventory_info']:
                data['inventory_info']['inventory_asset_account_id'] = validate_account_id(
                    data['inventory_info']['inventory_asset_account_id'],
                    'inventory'
                )
        
        # Update the data
        deep_update(updated_data, data)
        
        # Validate if type is being changed
        if 'type' in data:
            errors = validate_product(updated_data)
            if errors:
                return jsonify({"error": {"message": errors['error']}}), 400
        
        # Set timestamps
        now = datetime.utcnow().date().isoformat()
        updated_data['updated_at'] = now
        
        # Update product
        product = Product.from_dict(updated_data)
        products[product_index] = product.to_dict()
        
        # Update summary
        products_data['summary'] = update_summary(products).to_dict()
        products_data['products'] = products
        
        # Save to file
        if save_products(products_data):
            return jsonify(product.to_dict())
        else:
            return jsonify({"error": {"message": "Failed to save product"}}), 500
            
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@products_bp.route('/delete/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        # Load data
        products_data = load_products()
        products = products_data.get('products', [])
        
        # Find and remove product
        initial_count = len(products)
        products = [p for p in products if p.get('id') != product_id]
        
        if len(products) == initial_count:
            return jsonify({"error": {"message": "Product not found"}}), 404
        
        # Update data
        products_data['products'] = products
        products_data['summary'] = update_summary(products).to_dict()
        
        # Save to file
        if save_products(products_data):
            return '', 204
        else:
            return jsonify({"error": {"message": "Failed to delete product"}}), 500
            
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500