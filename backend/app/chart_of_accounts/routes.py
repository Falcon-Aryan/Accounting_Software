from flask import Blueprint, jsonify, request
from app.data_models.coa_types import ACCOUNT_TYPE, DETAILS_TYPE
from ..auth.decorators import require_auth
from .models import Account

chart_of_accounts_bp = Blueprint('chart_of_accounts', __name__)

@chart_of_accounts_bp.route('/create_account', methods=['POST'])
@require_auth
def create_account():
    """Create a new account in the chart of accounts"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['account_name', 'account_type', 'account_subtype', 'account_number']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
            
        # Validate account type and subtype
        if data['account_type'] not in ACCOUNT_TYPE:
            return jsonify({'error': f"Invalid account type: {data['account_type']}"}), 400
            
        if data['account_subtype'] not in DETAILS_TYPE[data['account_type']]:
            return jsonify({'error': f"Invalid account subtype for {data['account_type']}: {data['account_subtype']}"}), 400
            
        # Create account
        try:
            account = Account.create_account(
                user_id=request.headers.get('X-Appwrite-User-ID'),
                account_name=data['account_name'],
                account_type=data['account_type'],
                account_subtype=data['account_subtype'],
                account_number=data['account_number'],
                description=data.get('description'),
                opening_balance=float(data.get('opening_balance', 0.0))
            )
            return jsonify(account.to_dict()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/get_accounts', methods=['GET'])
@require_auth
def get_accounts():
    """Get all accounts for the current user"""
    try:
        accounts = Account.get_accounts_by_user(request.headers.get('X-Appwrite-User-ID'))
        return jsonify([account.to_dict() for account in accounts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/get_account/<account_id>', methods=['GET'])
@require_auth
def get_account(account_id):
    """Get details of a specific account"""
    try:
        account = Account.get_account_by_id(account_id, request.headers.get('X-Appwrite-User-ID'))
        return jsonify(account.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/update_account/<account_id>', methods=['PATCH'])
@require_auth
def update_account(account_id):
    """Update account details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # If updating account type or subtype, validate them
        if 'account_type' in data:
            if data['account_type'] not in ACCOUNT_TYPE:
                return jsonify({'error': f"Invalid account type: {data['account_type']}"}), 400
                
            if 'account_subtype' in data and data['account_subtype'] not in DETAILS_TYPE[data['account_type']]:
                return jsonify({'error': f"Invalid account subtype for {data['account_type']}: {data['account_subtype']}"}), 400
                
        # Convert opening_balance and current_balance to float if present
        if 'opening_balance' in data:
            data['opening_balance'] = float(data['opening_balance'])
        if 'current_balance' in data:
            data['current_balance'] = float(data['current_balance'])
            
        account = Account.update_account(account_id, request.headers.get('X-Appwrite-User-ID'), data)
        return jsonify(account.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/delete_account/<account_id>', methods=['DELETE'])
@require_auth
def delete_account(account_id):
    """Delete an account"""
    try:
        Account.delete_account(account_id, request.headers.get('X-Appwrite-User-ID'))
        return jsonify({'message': 'Account deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chart_of_accounts_bp.route('/account_types', methods=['GET'])
def get_account_types():
    """Get all valid account types and their subtypes"""
    return jsonify({
        'account_types': list(ACCOUNT_TYPE),
        'detail_types': DETAILS_TYPE
    }), 200

@chart_of_accounts_bp.route('/account_subtypes/<account_type>', methods=['GET'])
def get_account_subtypes(account_type):
    """Get valid subtypes for a specific account type"""
    if account_type not in ACCOUNT_TYPE:
        return jsonify({'error': f"Invalid account type: {account_type}"}), 400
    return jsonify({
        'account_type': account_type,
        'subtypes': DETAILS_TYPE[account_type]
    }), 200