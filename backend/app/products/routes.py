from flask import Blueprint, jsonify, request
from ..auth.decorators import require_auth
from .models import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/create_product', methods=['POST'])
@require_auth
def create_product():
    """Create a new physical product"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields (SKU is now optional)
        required_fields = ['name', 'price', 'stock']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
            
        # Create product with user_id from authenticated user
        try:
            product = Product.create_product(
                user_id=request.user.user_id,
                name=data['name'],
                price=data['price'],
                stock=data['stock'],
                sku=data.get('sku'),  # SKU is now optional
                description=data.get('description'),
                category=data.get('category')
            )
            return jsonify(product.to_dict()), 201
        except Exception as e:
            if "Product with SKU" in str(e):
                return jsonify({'error': str(e)}), 409  # HTTP 409 Conflict
            raise
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/get_products', methods=['GET'])
@require_auth
def get_products():
    """Get all products for the current user"""
    try:
        products = Product.get_products_by_user(request.user.user_id)
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/get_product/<product_id>', methods=['GET'])
@require_auth
def get_product(product_id):
    """Get details of a specific product"""
    try:
        product = Product.get_product(product_id, request.user.user_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/update_product/<product_id>', methods=['PATCH'])
@require_auth
def update_product(product_id):
    """Update product details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        product = Product.update_product(
            product_id=product_id,
            user_id=request.user.user_id,
            data=data
        )
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@products_bp.route('/delete_product/<product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    """Delete a product"""
    try:
        success = Product.delete_product(product_id, request.user.user_id)
        if not success:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400