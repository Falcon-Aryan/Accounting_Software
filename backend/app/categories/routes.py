# backend/app/categories/routes.py

from flask import Blueprint, jsonify, request
from ..auth.decorators import require_auth
from ..products.models import Product
from ..services.models import Service
from typing import Dict, List

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/get_by_category/<category>', methods=['GET'])
@require_auth
def get_by_category(category: str):
    """Get all products and services in a specific category"""
    try:
        # Get products in this category
        products = Product.get_products_by_category(request.user.user_id, category)
        
        # Get services in this category
        services = Service.get_services_by_category(request.user.user_id, category)
        
        return jsonify({
            'products': [product.to_dict() for product in products],
            'services': [service.to_dict() for service in services]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@categories_bp.route('/get_all_categories', methods=['GET'])
@require_auth
def get_all_categories():
    """Get a list of all unique categories used by the user"""
    try:
        # Get all products and services
        products = Product.get_products_by_user(request.user.user_id)
        services = Service.get_services_by_user(request.user.user_id)
        
        # Extract categories
        categories = set()
        for product in products:
            categories.update(product.category)
        for service in services:
            categories.update(service.category)
        
        return jsonify({
            'categories': sorted(list(categories))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400