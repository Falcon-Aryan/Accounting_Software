from flask import jsonify, request
from app.customers import customers_bp
from app.customers.models import Customer, Address
import uuid
from datetime import datetime
from typing import Dict, Optional

def validate_address(data: Dict) -> Optional[Dict]:
    required_fields = ['street', 'city', 'state', 'postal_code', 'country']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {'error': f'Missing required address fields: {", ".join(missing_fields)}'}
    return None

def validate_customer(data: Dict, for_update: bool = False) -> Optional[Dict]:
    if not for_update:
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'billing_address']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {'error': f'Missing required fields: {", ".join(missing_fields)}'}

    if 'billing_address' in data:
        error = validate_address(data['billing_address'])
        if error:
            return {'error': f'Invalid billing address: {error["error"]}'}

    if 'shipping_address' in data and data.get('use_billing_for_shipping') is False:
        error = validate_address(data['shipping_address'])
        if error:
            return {'error': f'Invalid shipping address: {error["error"]}'}

    return None

@customers_bp.route('/list_customers', methods=['GET'])
def get_customers():
    customers = Customer.get_all()
    if not customers:
        return jsonify({"message": "No customers found", "customers": []})
    return jsonify({"message": f"Found {len(customers)} customers", "customers": [customer.to_dict() for customer in customers]})

@customers_bp.route('/get_customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify({"message": "Customer found", "customer": customer.to_dict()})

@customers_bp.route('/create_customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    
    # Validate request data
    error = validate_customer(data)
    if error:
        return jsonify(error), 400

    # Check if customer already exists
    if Customer.exists(data['first_name'], data['last_name']):
        return jsonify({'error': 'A customer with this name already exists'}), 400

    # Create Address objects
    billing_address = Address(**data['billing_address'])
    shipping_address = None
    if not data.get('use_billing_for_shipping', True) and 'shipping_address' in data:
        shipping_address = Address(**data['shipping_address'])

    # Create new customer with 8-character ID
    customer = Customer(
        id=Customer.generate_customer_id(),
        customer_no=Customer.get_next_number(),
        first_name=data['first_name'],
        last_name=data['last_name'],
        company_name=data.get('company_name'),
        email=data['email'],
        phone=data['phone'],
        website=data.get('website'),
        billing_address=billing_address,
        shipping_address=shipping_address,
        use_billing_for_shipping=data.get('use_billing_for_shipping', True)
    )
    
    customer.save()
    return jsonify({"message": "Customer created successfully", "customer": customer.to_dict()}), 201

@customers_bp.route('/update_customer/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    
    # Validate request data
    error = validate_customer(data, for_update=True)
    if error:
        return jsonify(error), 400

    # Update customer fields
    if 'first_name' in data:
        customer.first_name = data['first_name']
    if 'last_name' in data:
        customer.last_name = data['last_name']
    if 'company_name' in data:
        customer.company_name = data['company_name']
    if 'email' in data:
        customer.email = data['email']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'website' in data:
        customer.website = data['website']

    # Update billing address if provided
    if 'billing_address' in data:
        customer.billing_address = Address(**data['billing_address'])

    # Update shipping preferences and address
    if 'use_billing_for_shipping' in data:
        customer.use_billing_for_shipping = data['use_billing_for_shipping']
        if not customer.use_billing_for_shipping and 'shipping_address' in data:
            customer.shipping_address = Address(**data['shipping_address'])
        elif customer.use_billing_for_shipping:
            customer.shipping_address = None

    customer.save()
    return jsonify({"message": "Customer updated successfully", "customer": customer.to_dict()})

@customers_bp.route('/delete_customer/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    customer.delete()
    return jsonify({"message": "Customer deleted successfully"}), 200

@customers_bp.route('/next_number', methods=['GET'])
def get_next_customer_number():
    return jsonify({"message": "Next customer number retrieved successfully", "next_number": Customer.get_next_number()})

@customers_bp.route('/summary', methods=['GET'])
def get_customer_summary():
    customers = Customer.get_all()
    return jsonify({"message": "Customer summary retrieved successfully", "total": len(customers), "recent": [c.to_dict() for c in sorted(customers, key=lambda x: x.created_at, reverse=True)[:5]]})
