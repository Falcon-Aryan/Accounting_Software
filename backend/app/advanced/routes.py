from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Dict, Any

from .models import Advanced
from ..auth.decorators import require_auth

advanced_bp = Blueprint('advanced', __name__)

@advanced_bp.route('/create_advanced', methods=['POST'])
@require_auth
def create_advanced(user_id: str):
    """Create advanced settings for a user
    
    Request body should contain advanced settings fields as defined in models.py.
    All optional fields will use defaults if not provided.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Add user_id and timestamps
        data['user_id'] = user_id
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()

        # Create settings
        settings = Advanced.create_settings(**data)
        
        return jsonify({
            'message': 'Advanced settings created successfully',
            'settings': settings.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create advanced settings: {str(e)}'}), 500

@advanced_bp.route('/get_advanced', methods=['GET'])
@require_auth
def get_advanced(user_id: str):
    """Get advanced settings for a user
    
    Returns 404 if no settings exist for the user.
    """
    try:
        settings = Advanced.get_settings(user_id)
        if not settings:
            return jsonify({'error': 'Advanced settings not found'}), 404

        return jsonify(settings.to_dict()), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get advanced settings: {str(e)}'}), 500

@advanced_bp.route('/update_advanced', methods=['PATCH'])
@require_auth
def update_advanced(user_id: str):
    """Update advanced settings for a user
    
    Request body should contain only the fields to update.
    Returns 404 if no settings exist for the user.
    """
    try:
        # Get existing settings
        settings = Advanced.get_settings(user_id)
        if not settings:
            return jsonify({'error': 'Advanced settings not found'}), 404

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update timestamps
        data['updated_at'] = datetime.utcnow().isoformat()

        # Update settings with new data
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        # Save updates
        updated_settings = settings.update()
        
        return jsonify({
            'message': 'Advanced settings updated successfully',
            'settings': updated_settings.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update advanced settings: {str(e)}'}), 500

@advanced_bp.route('/delete_advanced', methods=['DELETE'])
@require_auth
def delete_advanced(user_id: str):
    """Delete advanced settings for a user
    
    Returns 404 if no settings exist for the user.
    """
    try:
        # Get existing settings
        settings = Advanced.get_settings(user_id)
        if not settings:
            return jsonify({'error': 'Advanced settings not found'}), 404

        # Delete settings
        Advanced.delete_settings(settings.document_id)
        
        return jsonify({
            'message': 'Advanced settings deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to delete advanced settings: {str(e)}'}), 500