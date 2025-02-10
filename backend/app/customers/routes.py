from flask import Blueprint, jsonify, request
from .models import Customer
from ..auth.decorators import require_auth

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/create_customer', methods=['POST'])
@require_auth
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'customer_email', 'phone',
                         'billing_street', 'billing_city', 'billing_state',
                         'billing_postal_code', 'billing_country']
                         
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
            
        # Create customer with user_id from authenticated user
        try:
            customer = Customer.create_customer(
                user_id=request.user.user_id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                customer_email=data['customer_email'],
                phone=data['phone'],
                billing_street=data['billing_street'],
                billing_city=data['billing_city'],
                billing_state=data['billing_state'],
                billing_postal_code=data['billing_postal_code'],
                billing_country=data['billing_country'],
                company_name=data.get('company_name'),
                website=data.get('website'),
                use_billing_for_shipping=data.get('use_billing_for_shipping', True),
                shipping_street=data.get('shipping_street'),
                shipping_city=data.get('shipping_city'),
                shipping_state=data.get('shipping_state'),
                shipping_postal_code=data.get('shipping_postal_code'),
                shipping_country=data.get('shipping_country')
            )
            return jsonify(customer.to_dict()), 201
        except Exception as e:
            if "Customer already exists" in str(e):
                return jsonify({'error': str(e)}), 409  # HTTP 409 Conflict
            raise
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@customers_bp.route('/get_customers', methods=['GET'])
@require_auth
def get_customers():
    """Get all customers"""
    try:
        # Get all customers for current user
        customers = Customer.get_customers_by_user(request.user.user_id)
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@customers_bp.route('/get_customer/<customer_id>', methods=['GET'])
@require_auth
def get_customer(customer_id):
    """Get details of a specific customer"""
    try:
        customer = Customer.get_customer(customer_id, request.user.user_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
            
        return jsonify(customer.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@customers_bp.route('/update_customer/<customer_id>', methods=['PATCH'])
@require_auth
def update_customer(customer_id):
    """Update customer details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        customer = Customer.update_customer(
            customer_id=customer_id,
            user_id=request.user.user_id,
            data=data
        )
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
            
        return jsonify(customer.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@customers_bp.route('/delete_customer/<customer_id>', methods=['DELETE'])
@require_auth
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        success = Customer.delete_customer(customer_id, request.user.user_id)
        if not success:
            return jsonify({'error': 'Customer not found'}), 404
            
        return jsonify({'message': 'Customer deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
