from flask import Blueprint, jsonify, request
from .models import Vendor
from ..auth.decorators import require_auth

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/create_vendor', methods=['POST'])
@require_auth
def create_vendor():
    """Create a new vendor"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['company_name', 'contact_name', 'vendor_email', 'phone',
                         'billing_street', 'billing_city', 'billing_state',
                         'billing_postal_code', 'billing_country']
                         
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
            
        # Create vendor with user_id from authenticated user
        try:
            vendor = Vendor.create_vendor(
                user_id=request.user.user_id,
                company_name=data['company_name'],
                contact_name=data['contact_name'],
                vendor_email=data['vendor_email'],
                phone=data['phone'],
                billing_street=data['billing_street'],
                billing_city=data['billing_city'],
                billing_state=data['billing_state'],
                billing_postal_code=data['billing_postal_code'],
                billing_country=data['billing_country'],
                website=data.get('website'),
                payment_terms=data.get('payment_terms')
            )
            return jsonify(vendor.to_dict()), 201
        except Exception as e:
            if "Vendor already exists" in str(e):
                return jsonify({'error': str(e)}), 409  # HTTP 409 Conflict
            raise
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@vendors_bp.route('/get_vendors', methods=['GET'])
@require_auth
def get_vendors():
    """Get all vendors"""
    try:
        # Get all vendors for current user
        vendors = Vendor.get_vendors_by_user(request.user.user_id)
        return jsonify([vendor.to_dict() for vendor in vendors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@vendors_bp.route('/get_vendor/<vendor_id>', methods=['GET'])
@require_auth
def get_vendor(vendor_id):
    """Get details of a specific vendor"""
    try:
        vendor = Vendor.get_vendor(vendor_id, request.user.user_id)
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
            
        return jsonify(vendor.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@vendors_bp.route('/update_vendor/<vendor_id>', methods=['PATCH'])
@require_auth
def update_vendor(vendor_id):
    """Update vendor details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        vendor = Vendor.update_vendor(
            vendor_id=vendor_id,
            user_id=request.user.user_id,
            data=data
        )
        
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
            
        return jsonify(vendor.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@vendors_bp.route('/delete_vendor/<vendor_id>', methods=['DELETE'])
@require_auth
def delete_vendor(vendor_id):
    """Delete a vendor"""
    try:
        success = Vendor.delete_vendor(vendor_id, request.user.user_id)
        if not success:
            return jsonify({'error': 'Vendor not found'}), 404
            
        return jsonify({'message': 'Vendor deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400