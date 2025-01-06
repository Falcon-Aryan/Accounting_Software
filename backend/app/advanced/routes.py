from flask import jsonify, request
from . import advanced_bp
from .models import AdvancedSettings
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
from app.transactions import routes as transactions_routes
from app.chart_of_accounts import routes as chart_of_accounts_routes
from firebase_admin import auth

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path for storing advanced settings data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DEFAULTS_DIR = os.path.join(DATA_DIR, 'defaults')
DEFAULT_ADVANCED_FILE = os.path.join(DEFAULTS_DIR, 'advanced.json')

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_id():
    """Get the user ID from the Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except:
        return None

def get_user_advanced_file(uid: str) -> str:
    """Get the path to a user's advanced settings file"""
    user_dir = os.path.join(DATA_DIR, uid)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, 'advanced.json')

# Advanced field enums
ADVANCED_ENUMS = {
    "fiscal_year_start": [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ],
    "income_tax_year_start": [
        "Same as fiscal year",
        "January"
    ],
    "accounting_methods": [
        "Accrual",
        "Cash"
    ],
    "tax_forms": [
        "Sole Proprietor (Form 1040)",
        "Partnership or limited liability company (Form 1065)",
        "Small Business corporation, two or more owners (Form 1120S)",
        "Corporation, one or more shareholders (Form 1120)",
        "Nonprofit organization (Form 990)",
        "Limited Liability",
        "Other (Please specify)"
    ],
    "tips_accounts": [
        "Cash on Hand",
        "Accounts Receivable"
    ],
    "date_formats": [
        "mm/dd/yyyy",
        "dd/mm/yyyy",
        "yyyy/mm/dd"
    ],
    "currencies": [
        "United States Dollar (USD)"
    ],
    "number_formats": [
        "#,###.##",
        "#.###,##",
        "# ###,##"
    ],
    "sign_out_after_inactivity": [
        "1 hour",
        "2 hours",
        "3 hours"
    ]
}

def load_advanced_data(uid: str = None) -> Dict:
    """Load advanced settings data from JSON file."""
    try:
        # First try to load user-specific settings if UID is provided
        if uid:
            user_file = get_user_advanced_file(uid)
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    return json.load(f)

        # If no user file exists, load from defaults
        if os.path.exists(DEFAULT_ADVANCED_FILE):
            with open(DEFAULT_ADVANCED_FILE, 'r') as f:
                data = json.load(f)
                if uid:  # If this is for a user, save it to their file
                    save_advanced_data(data, uid)
                return data

        # If no default file exists, create with basic settings
        default_data = {
            "accounting": {
                "fiscal_year_start": "January",
                "income_tax_year_start": "Same as fiscal year",
                "accounting_method": "Accrual",
                "close_the_books": False
            },
            "company": {
                "tax_form": "Sole Proprietor (Form 1040)"
            },
            "chart_of_accounts": {
                "enable_account_numbers": True,
                "tips_account": "Tips Payable"
            },
            "categories": {
                "track_classes": False,
                "track_locations": False
            },
            "automation": {
                "pre_fill_forms": True,
                "apply_credits_automatically": True,
                "invoice_unbilled_activity": False,
                "apply_bill_payments_automatically": True
            },
            "projects": {
                "organize_job_activity": False
            },
            "currency": {
                "home_currency": "USD",
                "multicurrency": False
            },
            "other_preferences": {
                "date_format": "MM/DD/YYYY",
                "currency_format": "$#,###.##",
                "customer_label": "Customer",
                "duplicate_check_warning": True,
                "vendor_bill_warning": True,
                "duplicate_journal_warning": True,
                "sign_out_after_inactivity": "30 minutes"
            }
        }
        
        # Save default data
        os.makedirs(os.path.dirname(DEFAULT_ADVANCED_FILE), exist_ok=True)
        with open(DEFAULT_ADVANCED_FILE, 'w') as f:
            json.dump(default_data, f, indent=2)
            
        if uid:  # If this is for a user, save it to their file
            save_advanced_data(default_data, uid)
            
        return default_data
        
    except Exception as e:
        logger.error(f"Error loading advanced settings: {str(e)}")
        return {}

def save_advanced_data(data: Dict, uid: str = None) -> None:
    """Save advanced settings data to JSON file"""
    try:
        # If UID is provided, save to user's file
        if uid:
            file_path = get_user_advanced_file(uid)
        else:
            file_path = DEFAULT_ADVANCED_FILE
            
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving advanced settings: {str(e)}")
        raise

@advanced_bp.route('/get_advanced', methods=['GET'])
def get_advanced():
    """Retrieve advanced settings or specific attributes"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load settings from user's file
        settings = load_advanced_data(uid)
        
        # Check for specific attributes in query params
        attributes = request.args.get('attributes')
        if attributes:
            requested_data = {}
            for attr in attributes.split(','):
                value = get_nested_attribute(settings, attr.strip())
                if value is not None:
                    requested_data[attr] = value
            return jsonify(requested_data)
            
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error retrieving advanced settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/create_advanced', methods=['POST'])
def create_advanced():
    """Create advanced settings"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Save new settings
        save_advanced_data(data, uid)
        return jsonify({'message': 'Advanced settings created successfully', 'settings': data})
    except Exception as e:
        logger.error(f"Error creating advanced settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/update_advanced', methods=['PUT'])
def update_advanced():
    """Update advanced settings"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Load current settings
        current_settings = load_advanced_data(uid)
        
        # Update settings
        updated_settings = current_settings.copy()
        deep_update(updated_settings, data)
        save_advanced_data(updated_settings, uid)
        
        return jsonify({
            'message': 'Advanced settings updated successfully',
            'settings': updated_settings
        })
    except Exception as e:
        logger.error(f"Error updating advanced settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/delete_advanced', methods=['DELETE'])
def delete_advanced():
    """Reset advanced settings"""
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Load default settings
        default_settings = load_advanced_data()
        
        # Save default settings to user's file
        save_advanced_data(default_settings, uid)
        
        return jsonify({
            'message': 'Advanced settings reset to defaults successfully',
            'settings': default_settings
        })
    except Exception as e:
        logger.error(f"Error resetting advanced settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/get_field_options', methods=['GET'])
def get_field_options():
    """Get available options for advanced settings fields"""
    return jsonify(ADVANCED_ENUMS)

def deep_update(original, update):
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def get_nested_attribute(data, path):
    """Get nested attribute from dictionary using dot notation"""
    try:
        keys = path.split('.')
        value = data
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return None

def validate_fiscal_year_change(current_settings: Dict, new_settings: Dict) -> Optional[str]:
    """Validate fiscal year changes"""
    return None

def validate_accounting_method_change(current_settings: Dict, new_settings: Dict) -> Optional[str]:
    """Validate accounting method changes"""
    return None
