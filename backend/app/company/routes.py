from flask import jsonify, request
from . import company_bp
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional
import re
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path for storing company data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
COMPANY_DATA_FILE = os.path.join(DATA_DIR, 'company.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Company field enums
COMPANY_ENUMS = {
    "identity_types": [
        "SSN",
        "EIN"
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
    "states": [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", 
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", 
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
        "Wisconsin", "Wyoming"
    ]
}

# Validation patterns
PATTERNS = {
    'tax_id': r'^\d{2}-\d{7}$',
    'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
    'phone': r'^\+?[\d\s-]{10,}$',
    'zip': r'^\d{5}(-\d{4})?$'
}

def validate_company_data(data: Dict) -> Optional[str]:
    """Validate company data"""
    try:
        # Required fields
        if not data.get('company_name_info', {}).get('company_name'):
            return "Company name is required"
            
        # Tax ID format
        tax_id = data.get('company_name_info', {}).get('tax_id')
        if tax_id and not re.match(PATTERNS['tax_id'], tax_id):
            return "Tax ID must be in format XX-XXXXXXX"
            
        # Email format
        email = data.get('contact_info', {}).get('company_email')
        if email and not re.match(PATTERNS['email'], email):
            return "Invalid email format"
            
        # Phone format
        phone = data.get('contact_info', {}).get('company_phone')
        if phone and not re.match(PATTERNS['phone'], phone):
            return "Invalid phone number format"
            
        # ZIP code format
        for address in ['company_address', 'legal_address']:
            zip_code = data.get('Address', {}).get(address, {}).get('zip_code')
            if zip_code and not re.match(PATTERNS['zip'], zip_code):
                return f"Invalid ZIP code format for {address}"
                
        return None
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return f"Validation error: {str(e)}"

def create_audit_log(action: str, data: Dict) -> None:
    """Create an audit log entry directly in company.json"""
    try:
        # Load current company data
        company_data = {}
        if os.path.exists(COMPANY_DATA_FILE):
            with open(COMPANY_DATA_FILE, 'r') as f:
                company_data = json.load(f)
        
        # Initialize audit log array if it doesn't exist
        if 'audit_log' not in company_data:
            company_data['audit_log'] = []
        
        # Create new audit entry
        now = datetime.utcnow().date().isoformat()
        log_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': now,
            'action': action,
            'data': data
        }
        
        # Add to audit log
        company_data['audit_log'].append(log_entry)
        
        # Save updated company data
        with open(COMPANY_DATA_FILE, 'w') as f:
            json.dump(company_data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")

def load_company_data():
    """Load company data from JSON file"""
    try:
        if os.path.exists(COMPANY_DATA_FILE):
            with open(COMPANY_DATA_FILE, 'r') as file:
                data = json.load(file)
                # If file is empty or just contains {}, return default template
                if not data:
                    data = {
                        "company_name_info": {
                            "company_name": "",
                            "legal_name": "",
                            "same_as_company_name": False,
                            "identity": "",
                            "tax_id": ""
                        },
                        "company_type": {
                            "tax_form": "",
                            "industry": ""
                        },
                        "contact_info": {
                            "company_email": "",
                            "customer_facing_email": "",
                            "same_as_company_email": False,
                            "company_phone": "",
                            "website": ""
                        },
                        "Address": {
                            "company_address": {
                                "street": "",
                                "city": "",
                                "state": "",
                                "zip_code": "",
                                "country": ""
                            },
                            "legal_address": {
                                "street": "",
                                "city": "",
                                "state": "",
                                "zip_code": "",
                                "country": ""
                            },
                            "same_as_company_address": False
                        }
                    }
                    save_company_data(data)
                return data
    except Exception as e:
        print(f"Error loading company data: {str(e)}")
    return None

def save_company_data(data):
    """Save company data to JSON file"""
    try:
        with open(COMPANY_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving company data: {str(e)}")
        return False

def deep_update(original, update):
    """Recursively update nested dictionaries"""
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def apply_boolean_logic(company_data):
    """Apply boolean logic for same_as fields"""
    # Handle company name logic
    if company_data.get('company_name_info', {}).get('same_as_company_name'):
        company_data['company_name_info']['legal_name'] = company_data['company_name_info']['company_name']

    # Handle email logic
    if company_data.get('contact_info', {}).get('same_as_company_email'):
        company_data['contact_info']['customer_facing_email'] = company_data['contact_info']['company_email']

    # Handle address logic
    if company_data.get('Address', {}).get('same_as_company_address'):
        company_data['Address']['legal_address'] = company_data['Address']['company_address']

    return company_data

def get_nested_attribute(data, path):
    """Get nested attribute from dictionary using dot notation
    Example: get_nested_attribute(data, "Address.company_address.country")
    """
    try:
        for key in path.split('.'):
            data = data[key]
        return data
    except (KeyError, TypeError):
        return None

@company_bp.route('/create_company', methods=['POST'])
def create_company():
    """Create a new company"""
    try:
        company_data = request.get_json()
        
        # Check if company already exists
        existing_company = load_company_data()
        if existing_company:
            return jsonify({
                'success': False,
                'message': 'Company already exists'
            }), 409

        # Validate required fields
        required_fields = ['company_name_info', 'company_type', 'contact_info', 'Address']
        for field in required_fields:
            if field not in company_data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Validate company data
        validation_error = validate_company_data(company_data)
        if validation_error:
            return jsonify({
                'success': False,
                'message': validation_error
            }), 400

        # Apply boolean logic
        apply_boolean_logic(company_data)
        
        # Save to file
        if save_company_data(company_data):
            # Create audit log
            create_audit_log('create', company_data)
            
            logger.info(f"Company created successfully")
            return jsonify({
                'success': True,
                'message': 'Company created successfully',
                'company': company_data
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save company data'
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating company: {str(e)}'
        }), 400

@company_bp.route('/get_company', methods=['GET'])
def get_company():
    """Retrieve company details or specific attributes"""
    company_data = load_company_data()
    
    if not company_data:
        return jsonify({
            'error': 'Company not found'
        }), 404

    # Check if specific attribute is requested
    attribute = request.args.get('attribute')
    if attribute:
        value = get_nested_attribute(company_data, attribute)
        if value is not None:
            return jsonify({
                attribute: value
            }), 200
        else:
            return jsonify({
                'error': f'Attribute {attribute} not found'
            }), 404

    # Return full company data if no specific attribute is requested
    return jsonify(company_data), 200

@company_bp.route('/update_company', methods=['PATCH'])
def update_company():
    """Update company details"""
    try:
        update_data = request.get_json()
        existing_company = load_company_data()

        if not existing_company:
            return jsonify({
                'error': 'Company not found'
            }), 404

        # Validate company data
        validation_error = validate_company_data(update_data)
        if validation_error:
            return jsonify({
                'error': validation_error
            }), 400

        # Use deep update
        deep_update(existing_company, update_data)
        
        # Apply boolean logic after update
        existing_company = apply_boolean_logic(existing_company)

        # Save updated data
        if save_company_data(existing_company):
            # Create audit log
            create_audit_log('update', {
                'changes': update_data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Company data updated successfully")
            return jsonify({
                'message': 'Company updated successfully',
                'company': existing_company
            }), 200
        else:
            return jsonify({
                'error': 'Failed to save company data'
            }), 500

    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 400

@company_bp.route('/delete_company', methods=['DELETE'])
def delete_company():
    """Delete a company"""
    try:
        if os.path.exists(COMPANY_DATA_FILE):
            # Write an empty object to the file instead of deleting it
            with open(COMPANY_DATA_FILE, 'w') as file:
                json.dump({}, file)
            # Create audit log
            create_audit_log('delete', {})
            
            logger.info(f"Company deleted successfully")
            return jsonify({
                'message': 'Company deleted successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Company not found'
            }), 404
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@company_bp.route('/get_field_options', methods=['GET'])
def get_field_options():
    """Get available options for company fields"""
    return jsonify(COMPANY_ENUMS), 200
