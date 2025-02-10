from flask import Blueprint, request, jsonify
from ..auth.decorators import require_auth
from .models import PurchaseOrder, PurchaseOrderLineItem
from ..data_models.purchase_order_types import (
    PO_STATUSES,
    PO_STATUS_TRANSITIONS,
    PO_TYPES,
    PO_PAYMENT_TERMS,
    PO_LINE_ITEM_TYPES
)
from config.appwrite_setup import databases, DATABASE_ID
from appwrite.id import ID
from datetime import datetime

purchase_orders_bp = Blueprint('purchase_orders', __name__)

@purchase_orders_bp.route('/create_po', methods=['POST'])
@require_auth
def create_po():
    """Create a new purchase order"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Validate required fields
        required_fields = ['vendor_id', 'line_items', 'payment_terms']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Enhanced vendor validation
        is_valid, error_msg = PurchaseOrder.validate_vendor(user_id, data['vendor_id'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
            
        # Validate line items
        if not data['line_items'] or len(data['line_items']) == 0:
            return jsonify({'error': 'At least one line item is required'}), 400
            
        # Transform line item data to match new variable names
        transformed_line_items = []
        for item in data['line_items']:
            transformed_item = {
                'sku': item['sku'],
                'name': item['name'],
                'description': item.get('description'),
                'unit_cost': item['unit_cost'],
                'quantity': item['quantity'],
                'received_quantity': item.get('received_quantity', 0.0),
                'status': item.get('status', 'pending'),
                'expected_delivery_date': item.get('expected_delivery_date'),
                'last_received_date': item.get('last_received_date')
            }
            transformed_line_items.append(transformed_item)
            
        # Validate PO type
        po_type = data.get('po_type', 'standard')
        if po_type not in PO_TYPES:
            return jsonify({
                'error': f'Invalid PO type. Must be one of: {", ".join(PO_TYPES)}'
            }), 400
            
        # Validate payment terms
        if data['payment_terms'] not in PO_PAYMENT_TERMS:
            return jsonify({
                'error': f'Invalid payment terms. Must be one of: {", ".join(PO_PAYMENT_TERMS)}'
            }), 400
            
        # Create purchase order
        po = PurchaseOrder.create_po(
            user_id=user_id,
            vendor_id=data['vendor_id'],
            po_type=po_type,
            line_items=[PurchaseOrderLineItem.from_dict(item) for item in transformed_line_items],
            payment_terms=data['payment_terms'],
            notes=data.get('notes')
        )
        
        return jsonify(po.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        return jsonify({'error': f'Error creating purchase order: {str(e)}'}), 500

@purchase_orders_bp.route('/get_po/<po_id>', methods=['GET'])
@require_auth
def get_po(po_id):
    """Get a specific purchase order by PO ID"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        po = PurchaseOrder.get_po_by_id(po_id, user_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
            
        return jsonify(po.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_orders_bp.route('/list_pos', methods=['GET'])
@require_auth
def list_pos():
    """List all purchase orders for the current user"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        pos = PurchaseOrder.get_pos_by_user(user_id)
        return jsonify([po.to_dict() for po in pos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_orders_bp.route('/receive_items/<po_id>', methods=['POST'])
@require_auth
def receive_items(po_id):
    """Record receipt of items for a purchase order"""
    try:
        data = request.json
        if not data or 'items' not in data:
            return jsonify({'error': 'No items provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Get the purchase order
        po = PurchaseOrder.get_po_by_id(po_id, user_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
            
        # Validate PO status
        if po.status not in ['accepted', 'partially_received']:
            return jsonify({
                'error': f'Cannot receive items for PO in {po.status} status'
            }), 400
            
        # Process each received item
        for item in data['items']:
            if 'sku' not in item or 'quantity' not in item:
                return jsonify({
                    'error': 'Each item must have sku and quantity'
                }), 400
                
            try:
                po.receive_line_item(item['sku'], float(item['quantity']))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
        # Create or update products
        try:
            product_results = po.create_or_update_products()
            
            # Save PO changes
            updated_po = PurchaseOrder.update_po(
                po_id,
                user_id,
                po.to_dict()
            )
            
            if not updated_po:
                return jsonify({'error': 'Failed to update purchase order'}), 400
                
            return jsonify({
                'purchase_order': updated_po.to_dict(),
                'product_updates': product_results
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Error updating products: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_orders_bp.route('/update_po/<po_id>', methods=['PATCH'])
@require_auth
def update_po(po_id):
    """Update a purchase order"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Get the purchase order
        po = PurchaseOrder.get_po_by_id(po_id, user_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
            
        # Transform line items if provided
        if 'line_items' in data:
            if not isinstance(data['line_items'], list):
                return jsonify({'error': 'Line items must be a list'}), 400
                
            transformed_line_items = []
            for item in data['line_items']:
                transformed_item = {
                    'sku': item['sku'],
                    'name': item['name'],
                    'description': item.get('description'),
                    'unit_cost': item['unit_cost'],
                    'quantity': item['quantity'],
                    'received_quantity': item.get('received_quantity', 0.0),
                    'status': item.get('status', 'pending'),
                    'expected_delivery_date': item.get('expected_delivery_date'),
                    'last_received_date': item.get('last_received_date')
                }
                transformed_line_items.append(transformed_item)
                
            try:
                data['line_items'] = [PurchaseOrderLineItem.from_dict(item) for item in transformed_line_items]
            except ValueError as e:
                return jsonify({'error': f'Invalid line item data: {str(e)}'}), 400
                
        # Handle status update if provided
        if 'status' in data:
            try:
                po.update_status(data['status'])
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
        # Validate PO type if provided
        if 'po_type' in data and data['po_type'] not in PO_TYPES:
            return jsonify({
                'error': f'Invalid PO type. Must be one of: {", ".join(PO_TYPES)}'
            }), 400
            
        # Validate payment terms if provided
        if 'payment_terms' in data and data['payment_terms'] not in PO_PAYMENT_TERMS:
            return jsonify({
                'error': f'Invalid payment terms. Must be one of: {", ".join(PO_PAYMENT_TERMS)}'
            }), 400
            
        # Update vendor if provided
        if 'vendor_id' in data:
            is_valid, error_msg = PurchaseOrder.validate_vendor(user_id, data['vendor_id'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400
                
        # Update the purchase order
        updated_po = PurchaseOrder.update_po(po_id, user_id, data)
        if not updated_po:
            return jsonify({'error': 'Failed to update purchase order'}), 400
            
        return jsonify(updated_po.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_orders_bp.route('/update_po_status/<po_id>', methods=['PATCH'])
@require_auth
def update_po_status(po_id):
    """Update purchase order status"""
    try:
        data = request.json
        if not data or 'status' not in data:
            return jsonify({'error': 'Status not provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        new_status = data['status']
        
        # Get the purchase order
        po = PurchaseOrder.get_po_by_id(po_id, user_id)
        if not po:
            return jsonify({'error': 'Purchase order not found'}), 404
            
        # Validate status transition
        if new_status not in PO_STATUS_TRANSITIONS.get(po.status, []):
            return jsonify({
                'error': f'Invalid status transition from {po.status} to {new_status}'
            }), 400
            
        # Update status
        po.update_status(new_status)
        
        # Save changes
        updated_po = PurchaseOrder.update_po(
            po_id,
            user_id,
            {
                'status': new_status,
                'sent_at': po.sent_at,
                'accepted_at': po.accepted_at,
                'declined_at': po.declined_at,
                'received_at': po.received_at
            }
        )
        
        if not updated_po:
            return jsonify({'error': 'Failed to update purchase order status'}), 400
            
        return jsonify(updated_po.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_orders_bp.route('/delete_po/<po_id>', methods=['DELETE'])
@require_auth
def delete_po(po_id):
    """Delete a purchase order by PO ID"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        success = PurchaseOrder.delete_po(po_id, user_id)
        
        if not success:
            return jsonify({'error': 'Purchase order not found'}), 404
            
        return jsonify({'message': 'Purchase order deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400