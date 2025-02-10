from flask import Blueprint, jsonify, request
from .models import Company
from ..auth.decorators import require_auth

company_bp = Blueprint('company', __name__)

@company_bp.route('/create_company', methods=['POST'])
@require_auth
def create_company():
    """Create a new company"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = [
            'company_name', 'legal_name', 'identity_type', 'identity_number',
            'tax_form', 'industry', 'company_email', 'customer_facing_email',
            'company_phone', 'company_street', 'company_city', 'company_state',
            'company_postal_code', 'company_country'
        ]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        # Check if user already has a company
        existing_company = Company.get_company(request.user.user_id)
        if existing_company:
            return jsonify({'error': 'User already has a company'}), 409

        # Create company with user_id from authenticated user
        try:
            company = Company.create_company(
                user_id=request.user.user_id,
                company_name=data['company_name'],
                legal_name=data['legal_name'],
                identity_type=data['identity_type'],
                identity_number=data['identity_number'],
                tax_form=data['tax_form'],
                industry=data['industry'],
                company_email=data['company_email'],
                customer_facing_email=data['customer_facing_email'],
                company_phone=data['company_phone'],
                company_street=data['company_street'],
                company_city=data['company_city'],
                company_state=data['company_state'],
                company_postal_code=data['company_postal_code'],
                company_country=data['company_country'],
                same_as_company_name=data.get('same_as_company_name', True),
                same_as_company_email=data.get('same_as_company_email', True),
                website=data.get('website'),
                legal_street=data.get('legal_street'),
                legal_city=data.get('legal_city'),
                legal_state=data.get('legal_state'),
                legal_postal_code=data.get('legal_postal_code'),
                legal_country=data.get('legal_country'),
                same_as_company_address=data.get('same_as_company_address', True),
                status=data.get('status', 'active')
            )
            return jsonify(company.to_dict()), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/get_company', methods=['GET'])
@require_auth
def get_company():
    """Get company details for the authenticated user"""
    try:
        company = Company.get_company(request.user.user_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        return jsonify(company.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/update_company', methods=['PATCH'])
@require_auth
def update_company():
    """Update company details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get existing company
        company = Company.get_company(request.user.user_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Update company attributes
        for key, value in data.items():
            if hasattr(company, key):
                setattr(company, key, value)

        # Update the company
        try:
            updated_company = company.update()
            return jsonify(updated_company.to_dict()), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/delete_company', methods=['DELETE'])
@require_auth
def delete_company():
    """Delete company"""
    try:
        company = Company.get_company(request.user.user_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        Company.delete_company(company.document_id)
        return jsonify({'message': 'Company deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500