from flask import jsonify, request
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import random

from . import transactions_bp
from .models import Transaction, TransactionEntry

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def generate_transaction_id() -> str:
    """Generate a random transaction ID"""
    return f"TXN-{random.randint(10000, 99999)}"

def load_transactions() -> Dict:
    """Load transactions data from JSON file"""
    try:
        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading transactions data: {str(e)}")
    return {'transactions': []}

def save_transactions(data: Dict) -> bool:
    """Save transactions data to JSON file"""
    try:
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving transactions data: {str(e)}")
        return False

def create_transaction_direct(transaction_data: dict):
    """Create a new transaction directly from code (not via HTTP)"""
    try:
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Set dates
        now = datetime.utcnow().date().isoformat()
        transaction_data['date'] = transaction_data.get('date', now)
        transaction_data['created_at'] = now
        transaction_data['updated_at'] = now
        
        # Add metadata
        transaction_data['id'] = transaction_id
        transaction_data['status'] = transaction_data.get('status', 'draft')
        
        # Create and validate transaction
        transaction = Transaction.from_dict(transaction_data)
        is_valid, error = transaction.validate()
        if not is_valid:
            raise Exception(error)
        
        # Save transaction
        transactions_data = load_transactions()
        transactions_data['transactions'].append(transaction.to_dict())
        if not save_transactions(transactions_data):
            raise Exception('Failed to save transaction')
        
        return transaction.to_dict()
        
    except Exception as e:
        print(f"Error in create_transaction_direct: {str(e)}")
        raise

@transactions_bp.route('/list', methods=['GET'])
def list_transactions():
    """Get a paginated list of transactions with optional filters"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        account_id = request.args.get('account_id')

        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])

        # Apply filters
        filtered_transactions = transactions
        if start_date and start_date != '<date>':
            filtered_transactions = [t for t in filtered_transactions if t['date'] >= start_date]
        if end_date and end_date != '<date>':
            filtered_transactions = [t for t in filtered_transactions if t['date'] <= end_date]
        if status and status != '<string>':
            filtered_transactions = [t for t in filtered_transactions if t['status'] == status]
        if account_id and account_id != '<string>':
            filtered_transactions = [t for t in filtered_transactions 
                                  if any(e['accountId'] == account_id for e in t['entries'])]

        # Calculate pagination
        total = len(filtered_transactions)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_transactions = filtered_transactions[start_idx:end_idx]

        return jsonify({
            'transactions': paginated_transactions,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        })

    except Exception as e:
        return jsonify({'message': f'Error listing transactions: {str(e)}'}), 500

@transactions_bp.route('/create', methods=['POST'])
def create_transaction():
    """Create a new transaction via HTTP endpoint"""
    try:
        data = request.get_json()
        result = create_transaction_direct(data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'message': f'Error creating transaction: {str(e)}'}), 500

@transactions_bp.route('/get/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get details of a specific transaction"""
    try:
        # Load transactions
        data = load_transactions()
        
        # Find transaction
        transaction = next(
            (t for t in data.get('transactions', []) if t['id'] == transaction_id),
            None
        )
        
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404
            
        return jsonify(transaction)
        
    except Exception as e:
        return jsonify({'message': f'Error getting transaction: {str(e)}'}), 500

@transactions_bp.route('/patch/<transaction_id>', methods=['PATCH'])
def patch_transaction(transaction_id):
    """Update specific fields of a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                if t['status'] != 'draft':
                    return jsonify({
                        'message': 'Only draft transactions can be updated'
                    }), 400
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Update fields
        patch_data = request.get_json()
        current_transaction = transactions[transaction_index]
        current_transaction.update({
            k: v for k, v in patch_data.items()
            if k in ['date', 'description', 'reference', 'entries']
        })
        current_transaction['updated_at'] = datetime.utcnow().date().isoformat()
        
        # Validate updated transaction
        transaction = Transaction.from_dict(current_transaction)
        is_valid, error = transaction.validate()
        if not is_valid:
            return jsonify({'message': error}), 400
            
        # Save changes
        transactions[transaction_index] = transaction.to_dict()
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error updating transaction: {str(e)}'}), 500

@transactions_bp.route('/delete/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Remove transaction
        transactions.pop(transaction_index)
        
        # Save changes
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify({'message': 'Transaction deleted successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Error deleting transaction: {str(e)}'}), 500

@transactions_bp.route('/post/<transaction_id>', methods=['POST'])
def post_transaction(transaction_id):
    """Post a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Find transaction
        transaction_index = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Validate transaction
        transaction = Transaction.from_dict(transactions[transaction_index])
        is_valid, error = transaction.validate()
        if not is_valid:
            return jsonify({'message': error}), 400
            
        # Update status
        now = datetime.utcnow().date().isoformat()
        transaction.status = 'posted'
        transaction.posted_at = now
        transaction.updated_at = now
        
        # Save changes
        transactions[transaction_index] = transaction.to_dict()
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error posting transaction: {str(e)}'}), 500

@transactions_bp.route('/void/<transaction_id>', methods=['POST'])
def void_transaction(transaction_id):
    """Void a transaction"""
    try:
        # Load transactions
        data = load_transactions()
        transactions = data.get('transactions', [])
        
        # Get void reason
        void_data = request.get_json()
        if not void_data or 'reason' not in void_data:
            return jsonify({'message': 'Void reason is required'}), 400
            
        # Find transaction
        transaction_index = None
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index is None:
            return jsonify({'message': 'Transaction not found'}), 404
            
        # Update status
        now = datetime.utcnow().date().isoformat()
        transaction = Transaction.from_dict(transactions[transaction_index])
        transaction.status = 'void'
        transaction.voided_at = now
        transaction.updated_at = now
        
        # Save changes
        transactions[transaction_index] = transaction.to_dict()
        if not save_transactions(data):
            return jsonify({'message': 'Failed to save changes'}), 500
            
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        return jsonify({'message': f'Error voiding transaction: {str(e)}'}), 500
