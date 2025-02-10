from flask import Blueprint, request, jsonify
from ..auth.decorators import require_auth
from .models import Estimate, EstimateLineItem, ESTIMATE_STATUSES, PAYMENT_TERMS
from ..invoices.models import Invoice, InvoiceLineItem, INVOICE_STATUSES, PAYMENT_TERMS
from config.appwrite_setup import databases, DATABASE_ID
from appwrite.id import ID
from datetime import datetime

estimates_bp = Blueprint('estimates', __name__)

# Validate status transition
VALID_STATUS_TRANSITIONS = {
    'draft': ['sent'],
    'sent': ['accepted', 'declined', 'expired', 'draft'],
    'accepted': ['converted', 'draft'],
    'declined': ['draft'],
    'expired': ['draft'],
    'converted': ['draft']
}

@estimates_bp.route('/create_estimate', methods=['POST'])
@require_auth
def create_estimate():
    """Create a new estimate"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Validate required fields
        required_fields = ['customer_id', 'line_items', 'payment_terms']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Validate customer exists and belongs to user
        if not Estimate.validate_customer(user_id, data['customer_id']):
            return jsonify({
                'error': f'Customer {data["customer_id"]} not found or does not belong to user {user_id}'
            }), 400
            
        # Validate line items
        if not isinstance(data['line_items'], list) or not data['line_items']:
            return jsonify({'error': 'At least one line item is required'}), 400
            
        # Validate payment terms
        if data['payment_terms'] not in PAYMENT_TERMS:
            return jsonify({
                'error': f'Invalid payment terms. Must be one of: {", ".join(PAYMENT_TERMS)}'
            }), 400
            
        # Create and validate line items
        line_items = []
        for item_data in data['line_items']:
            try:
                # Infer type from item_id
                if 'item_id' not in item_data:
                    return jsonify({'error': 'Line item missing item_id field'}), 400
                    
                item_id = item_data['item_id']
                if item_id.startswith('PROD'):
                    item_data['type'] = 'product'
                    # Validate product exists and belongs to user
                    if not Estimate.validate_product(user_id, item_id):
                        return jsonify({
                            'error': f'Product {item_id} not found or does not belong to user {user_id}'
                        }), 400
                elif item_id.startswith('SERV'):
                    item_data['type'] = 'service'
                    # Validate service exists and belongs to user
                    if not Estimate.validate_service(user_id, item_id):
                        return jsonify({
                            'error': f'Service {item_id} not found or does not belong to user {user_id}'
                        }), 400
                else:
                    return jsonify({'error': f'Invalid item_id format: {item_id}. Must start with PROD or SERV'}), 400
                        
                line_items.append(EstimateLineItem.from_dict(item_data))
            except Exception as e:
                return jsonify({'error': f'Invalid line item data: {str(e)}'}), 400
            
        # Create estimate object with line items
        estimate = Estimate.create_estimate(
            user_id=user_id,
            customer_id=data['customer_id'],
            items=line_items,
            payment_terms=data['payment_terms']
        )
        
        # Create the estimate document
        estimate_doc = databases.create_document(
            database_id=DATABASE_ID,
            collection_id='estimates',
            document_id=ID.unique(),
            data=estimate.to_dict(for_appwrite=True)
        )
        
        return jsonify({
            "message": "Estimate created successfully", 
            "estimate": estimate_doc
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@estimates_bp.route('/get_estimate/<estimate_id>', methods=['GET'])
@require_auth
def get_estimate(estimate_id: str):
    """Get a specific estimate by estimate ID"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        estimate = Estimate.get_estimate_by_id(estimate_id, user_id)
        return jsonify(estimate.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@estimates_bp.route('/list_estimates', methods=['GET'])
@require_auth
def list_estimates():
    """List all estimates for the current user"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        estimates = Estimate.get_estimates_by_user(user_id)
        
        # Check expiration for all sent estimates
        for estimate in estimates:
            estimate.check_expiration()
            
        return jsonify({
            'estimates': [estimate.to_dict() for estimate in estimates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estimates_bp.route('/update_estimate/<estimate_id>', methods=['PATCH'])
@require_auth
def update_estimate(estimate_id):
    """Update an estimate by estimate ID"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Get the estimate
        estimate = Estimate.get_estimate_by_id(estimate_id, user_id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # Handle status update if provided
        if 'status' in data:
            try:
                estimate.update_status(data['status'], data.get('decline_reason'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
        # Update other fields if provided
        if 'customer_id' in data:
            # Validate new customer exists and belongs to user
            if not Estimate.validate_customer(user_id, data['customer_id']):
                return jsonify({
                    'error': f'Customer {data["customer_id"]} not found or does not belong to user {user_id}'
                }), 400
            estimate.customer_id = data['customer_id']
            
        if 'payment_terms' in data:
            if data['payment_terms'] not in PAYMENT_TERMS:
                return jsonify({
                    'error': f'Invalid payment terms. Must be one of: {", ".join(PAYMENT_TERMS)}'
                }), 400
            estimate.payment_terms = data['payment_terms']
            
        if 'line_items' in data:
            try:
                line_items = []
                for item_data in data['line_items']:
                    # Infer type from item_id
                    if 'item_id' not in item_data:
                        return jsonify({'error': 'Line item missing item_id field'}), 400
                        
                    item_id = item_data['item_id']
                    if item_id.startswith('PROD'):
                        item_data['type'] = 'product'
                        # Validate product exists and belongs to user
                        if not Estimate.validate_product(user_id, item_id):
                            return jsonify({
                                'error': f'Product {item_id} not found or does not belong to user {user_id}'
                            }), 400
                    elif item_id.startswith('SERV'):
                        item_data['type'] = 'service'
                        # Validate service exists and belongs to user
                        if not Estimate.validate_service(user_id, item_id):
                            return jsonify({
                                'error': f'Service {item_id} not found or does not belong to user {user_id}'
                            }), 400
                    else:
                        return jsonify({'error': f'Invalid item_id format: {item_id}. Must start with PROD or SERV'}), 400
                            
                    line_items.append(EstimateLineItem.from_dict(item_data))
                estimate.items = line_items
            except (KeyError, ValueError) as e:
                return jsonify({'error': f'Invalid line item data: {str(e)}'}), 400
                
        # Recalculate total
        estimate._calculate_total()
        
        # Update in database
        db = Estimate.get_database()
        if not estimate.document_id:
            return jsonify({'error': 'Document ID not found'}), 500
            
        # Convert to Appwrite format and update
        appwrite_data = estimate.to_dict(for_appwrite=True)
        result = db.update_document(
            database_id=DATABASE_ID,
            collection_id='estimates',
            document_id=estimate.document_id,
            data=appwrite_data
        )
        
        # Create response with updated estimate
        updated_estimate = Estimate.from_dict(result, document_id=result['$id'])
        
        return jsonify({
            'message': 'Estimate updated successfully',
            'estimate': updated_estimate.to_dict()
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estimates_bp.route('/delete_estimate/<estimate_id>', methods=['DELETE'])
@require_auth
def delete_estimate(estimate_id: str):
    """Delete an estimate by estimate ID"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        Estimate.delete_estimate(estimate_id, user_id)
        return jsonify({"message": "Estimate deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@estimates_bp.route('/convert_to_invoice/<estimate_id>', methods=['POST'])
@require_auth
def convert_to_invoice(estimate_id):
    """Convert an estimate to an invoice"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Get the estimate
        estimate = Estimate.get_estimate_by_id(estimate_id, user_id)
        if not estimate:
            return jsonify({'error': 'Estimate not found'}), 404
            
        # Check if estimate can be converted
        if estimate.status != 'accepted':
            return jsonify({'error': 'Only accepted estimates can be converted to invoices'}), 400
            
        if estimate.status == 'converted':
            return jsonify({'error': 'Estimate has already been converted to an invoice'}), 400
            
        # Convert estimate line items to invoice line items
        line_items = [
            InvoiceLineItem(
                type=item.type,
                item_id=item.item_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                description=item.description
            ) for item in estimate.items
        ]
        
        # Create new invoice with converted_from field
        invoice = Invoice.create_invoice(
            user_id=user_id,
            customer_id=estimate.customer_id,
            line_items=line_items,
            payment_terms=estimate.payment_terms,
            converted_from=estimate_id,
            notes=estimate.notes
        )
        
        # Save the invoice
        db = Invoice.get_database()
        invoice_dict = invoice.to_dict(for_appwrite=True)
        result = db.create_document(
            database_id=Invoice.DATABASE_ID,
            collection_id=Invoice.COLLECTION_ID,
            document_id=ID.unique(),
            data=invoice_dict
        )
        
        # Update estimate status to converted and save
        estimate.update_status('converted')
        estimate_db = Estimate.get_database()
        estimate_dict = estimate.to_dict(for_appwrite=True)
        estimate_result = estimate_db.update_document(
            database_id=Estimate.DATABASE_ID,
            collection_id='estimates',
            document_id=estimate.document_id,
            data=estimate_dict
        )
        
        return jsonify({
            'message': 'Estimate successfully converted to invoice',
            'invoice': Invoice.from_dict(result, document_id=result['$id']).to_dict(),
            'estimate': Estimate.from_dict(estimate_result, document_id=estimate_result['$id']).to_dict()
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
