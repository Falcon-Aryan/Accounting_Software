from flask import Blueprint, jsonify, request
from ..auth.decorators import require_auth
from .models import Service

services_bp = Blueprint('services', __name__)

@services_bp.route('/create_service', methods=['POST'])
@require_auth
def create_service():
    """Create a new service"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['name', 'price']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
            
        # Create service with user_id from authenticated user
        try:
            service = Service.create_service(
                user_id=request.user.user_id,
                name=data['name'],
                price=data['price'],
                duration=data.get('duration'),
                description=data.get('description'),
                category=data.get('category')
            )
            return jsonify(service.to_dict()), 201
        except Exception as e:
            raise
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/get_services', methods=['GET'])
@require_auth
def get_services():
    """Get all services for the current user"""
    try:
        services = Service.get_services_by_user(request.user.user_id)
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/get_service/<service_id>', methods=['GET'])
@require_auth
def get_service(service_id):
    """Get details of a specific service"""
    try:
        service = Service.get_service(service_id, request.user.user_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
            
        return jsonify(service.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/update_service/<service_id>', methods=['PATCH'])
@require_auth
def update_service(service_id):
    """Update service details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        service = Service.update_service(
            service_id=service_id,
            user_id=request.user.user_id,
            data=data
        )
        
        if not service:
            return jsonify({'error': 'Service not found'}), 404
            
        return jsonify(service.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/delete_service/<service_id>', methods=['DELETE'])
@require_auth
def delete_service(service_id):
    """Delete a service"""
    try:
        success = Service.delete_service(service_id, request.user.user_id)
        if not success:
            return jsonify({'error': 'Service not found'}), 404
            
        return jsonify({'message': 'Service deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400