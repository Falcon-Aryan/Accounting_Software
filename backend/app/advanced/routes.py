from flask import jsonify, request
from . import advanced_bp
from .models import AdvancedSettings
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
from app.transactions.routes import load_transactions
from app.chart_of_accounts.routes import load_accounts

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path for storing advanced settings data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ADVANCED_DATA_FILE = os.path.join(DATA_DIR, 'advanced.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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

def load_advanced_data():
    """Load advanced settings data from JSON file."""
    try:
        if os.path.exists(ADVANCED_DATA_FILE):
            with open(ADVANCED_DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            default_data = {
                "accounting": {
                    "fiscal_year_start": "",
                    "income_tax_year_start": "",
                    "accounting_method": "",
                    "close_the_books": False
                },
                "company_type": {
                    "tax_form": ""
                },
                "chart_of_accounts": {
                    "enable_account_numbers": False,
                    "tips_account": ""
                },
                "categories": {
                    "track_classes": False,
                    "track_locations": False
                },
                "automation": {
                    "pre_fill_forms": False,
                    "apply_credits_automatically": False,
                    "invoice_unbilled_activity": False,
                    "apply_bill_payments_automatically": False
                },
                "projects": {
                    "organize_job_activity": False
                },
                "currency": {
                    "home_currency": "United States Dollar",
                    "multicurrency": False
                },
                "other_preferences": {
                    "date_format": "",
                    "currency_format": "",
                    "customer_label": "",
                    "duplicate_check_warning": False,
                    "vendor_bill_warning": False,
                    "duplicate_journal_warning": False,
                    "sign_out_after_inactivity": ""
                }
            }
            with open(ADVANCED_DATA_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
            return default_data
    except Exception as e:
        print(f"Error loading advanced data: {e}")
        return None

def save_advanced_data(data):
    """Save advanced settings data to JSON file"""
    try:
        with open(ADVANCED_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving advanced settings data: {str(e)}")
        return False

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
        for key in path.split('.'):
            data = data[key]
        return data
    except (KeyError, TypeError):
        return None

def validate_fiscal_year_change(current_settings: Dict, new_settings: Dict) -> Optional[str]:
    """Validate fiscal year changes"""
    try:
        current_fy = current_settings.get('accounting', {}).get('fiscal_year_start')
        new_fy = new_settings.get('accounting', {}).get('fiscal_year_start')
        
        if current_fy and new_fy and current_fy != new_fy:
            # Check if there are any unposted transactions
            transactions = load_transactions().get('transactions', [])
            unposted = [t for t in transactions if t.get('status') == 'draft']
            
            if unposted:
                return "Cannot change fiscal year while there are unposted transactions"
                
        return None
        
    except Exception as e:
        logger.error(f"Fiscal year validation error: {str(e)}")
        return str(e)

def validate_accounting_method_change(current_settings: Dict, new_settings: Dict) -> Optional[str]:
    """Validate accounting method changes"""
    try:
        current_method = current_settings.get('accounting', {}).get('accounting_method')
        new_method = new_settings.get('accounting', {}).get('accounting_method')
        
        if current_method and new_method and current_method != new_method:
            # Check account balances
            accounts = load_accounts().get('accounts', [])
            has_balances = any(float(acc.get('balance', 0)) != 0 for acc in accounts)
            
            if has_balances:
                return "Cannot change accounting method while accounts have balances"
                
        return None
        
    except Exception as e:
        logger.error(f"Accounting method validation error: {str(e)}")
        return str(e)

def create_settings_backup() -> bool:
    """Create a backup of current settings"""
    try:
        backup_file = os.path.join(DATA_DIR, f'advanced_backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json')
        if os.path.exists(ADVANCED_DATA_FILE):
            with open(ADVANCED_DATA_FILE, 'r') as src, open(backup_file, 'w') as dst:
                json.dump(json.load(src), dst, indent=2)
        return True
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return False

@advanced_bp.route('/get_advanced', methods=['GET'])
def get_advanced():
    """Retrieve advanced settings or specific attributes"""
    advanced_data = load_advanced_data()
    
    if not advanced_data:
        return jsonify({
            'error': 'Advanced settings not found'
        }), 404

    # Check if specific attribute is requested
    attribute = request.args.get('attribute')
    if attribute:
        value = get_nested_attribute(advanced_data, attribute)
        if value is not None:
            return jsonify({
                attribute: value
            }), 200
        else:
            return jsonify({
                'error': f'Attribute {attribute} not found'
            }), 404

    return jsonify(advanced_data), 200

@advanced_bp.route('/create_advanced', methods=['POST'])
def create_advanced():
    """Create advanced settings"""
    try:
        data = request.get_json()
        
        # Validate data using model
        try:
            settings = AdvancedSettings.from_dict(data)
            advanced_data = settings.to_dict()
        except Exception as e:
            return jsonify({
                'error': f'Invalid data format: {str(e)}'
            }), 400

        # Check if settings already exist
        existing_settings = load_advanced_data()
        if existing_settings:
            return jsonify({
                'error': 'Advanced settings already exist'
            }), 409

        # Save advanced settings data
        if save_advanced_data(advanced_data):
            return jsonify({
                'message': 'Advanced settings created successfully',
                'settings': advanced_data
            }), 201
        else:
            return jsonify({
                'error': 'Failed to save advanced settings'
            }), 500

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400

@advanced_bp.route('/update_advanced', methods=['PATCH'])
def update_advanced():
    """Update advanced settings with validation and migration handling"""
    try:
        data = request.get_json()
        
        # Load current settings
        current_settings = load_advanced_data()
        
        # Validate fiscal year change
        fy_error = validate_fiscal_year_change(current_settings, data)
        if fy_error:
            return jsonify({'message': fy_error}), 400
            
        # Validate accounting method change
        method_error = validate_accounting_method_change(current_settings, data)
        if method_error:
            return jsonify({'message': method_error}), 400
            
        # Create backup
        if not create_settings_backup():
            return jsonify({'message': 'Failed to create backup'}), 500
            
        # Update settings
        deep_update(current_settings, data)
        
        # Save changes
        if save_advanced_data(current_settings):
            logger.info("Advanced settings updated successfully")
            return jsonify(current_settings)
        else:
            return jsonify({'message': 'Failed to save changes'}), 500
            
    except Exception as e:
        logger.error(f"Error updating advanced settings: {str(e)}")
        return jsonify({'message': f'Error updating settings: {str(e)}'}), 500

@advanced_bp.route('/delete_advanced', methods=['DELETE'])
def delete_advanced():
    """Reset advanced settings"""
    try:
        if os.path.exists(ADVANCED_DATA_FILE):
            # Write an empty object to the file instead of deleting it
            with open(ADVANCED_DATA_FILE, 'w') as file:
                json.dump({}, file)
            return jsonify({
                'message': 'Advanced settings reset successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Advanced settings not found'
            }), 404
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@advanced_bp.route('/get_field_options', methods=['GET'])
def get_field_options():
    """Get available options for advanced settings fields"""
    return jsonify(ADVANCED_ENUMS), 200
