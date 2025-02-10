from flask import Blueprint, request, jsonify
from ..auth.decorators import require_auth
from .models import Transaction, TransactionEntry, TRANSACTION_STATUSES, TRANSACTION_TYPES, VALID_STATUS_TRANSITIONS
from config.appwrite_setup import databases
from appwrite.query import Query
from appwrite.id import ID
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/create_transaction', methods=['POST'])
@require_auth
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['description', 'entries']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Parse and validate entries
        if not isinstance(data['entries'], list) or not data['entries']:
            return jsonify({'error': 'At least one entry is required'}), 400
            
        try:
            entries = []
            for entry_data in data['entries']:
                entry = TransactionEntry(
                    account_id=entry_data.get('account_id'),
                    debit_amount=float(entry_data.get('debit_amount', 0)),
                    credit_amount=float(entry_data.get('credit_amount', 0)),
                    description=entry_data.get('description')
                )
                entries.append(entry)
                
        except ValueError as e:
            return jsonify({'error': f'Invalid entry data: {str(e)}'}), 400
            
        # Create transaction
        transaction = Transaction.create_transaction(
            user_id=user_id,
            description=data['description'],
            entries=entries,
            transaction_type=data.get('type', 'journal_entry'),
            notes=data.get('notes')
        )
        
        # Save to database
        database = Transaction.get_database()
        result = database.create_document(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            document_id=ID.unique(),
            data=transaction.to_dict(for_appwrite=True)  # This ensures entries are JSON string
        )
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': transaction.to_dict()  # This returns entries as list for API response
        }), 201
        
    except Exception as e:
        print(f"Error in create_transaction: {str(e)}")  # Debug print
        return jsonify({'error': f'Error creating transaction: {str(e)}'}), 500

@transactions_bp.route('/get_transaction/<transaction_id>', methods=['GET'])
@require_auth
def get_transaction(transaction_id: str):
    """Get a specific transaction"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        database = Transaction.get_database()
        
        # Get transaction document
        result = database.list_documents(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            queries=[
                Query.equal('transaction_id', transaction_id),
                Query.equal('user_id', user_id)
            ]
        )
        
        if not result['documents']:
            return jsonify({'error': 'Transaction not found'}), 404
            
        transaction = Transaction.from_dict(result['documents'][0])
        return jsonify(transaction.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Error getting transaction: {str(e)}'}), 500

@transactions_bp.route('/get_transactions', methods=['GET'])
@require_auth
def get_user_transactions():
    """Get all transactions for the current user"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        database = Transaction.get_database()
        
        result = database.list_documents(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            queries=[Query.equal('user_id', user_id)]
        )
        
        transactions = [Transaction.from_dict(doc) for doc in result['documents']]
        return jsonify([t.to_dict() for t in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': f'Error getting transactions: {str(e)}'}), 500

@transactions_bp.route('/update_transaction/<transaction_id>', methods=['PATCH'])
@require_auth
def update_transaction(transaction_id: str):
    """Update a transaction"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = request.headers.get('X-Appwrite-User-ID')
        database = Transaction.get_database()
        
        # Get existing transaction
        result = database.list_documents(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            queries=[
                Query.equal('transaction_id', transaction_id),
                Query.equal('user_id', user_id)
            ]
        )
        
        if not result['documents']:
            return jsonify({'error': 'Transaction not found'}), 404
            
        transaction = Transaction.from_dict(result['documents'][0])
        
        # If transaction is not in draft status, only status changes are allowed
        if transaction.status != 'draft':
            non_status_fields = [field for field in data.keys() if field != 'status' and field != 'void_reason']
            if non_status_fields:
                return jsonify({
                    'error': f'Cannot update fields {", ".join(non_status_fields)} for non-draft transaction. Only status changes are allowed.'
                }), 400
        
        # Handle status change if present
        if 'status' in data:
            if data['status'] not in TRANSACTION_STATUSES:
                return jsonify({'error': f'Invalid status: {data["status"]}'}), 400
                
            void_reason = data.get('void_reason') if data['status'] == 'void' else None
            try:
                transaction.update_status(data['status'], void_reason)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        # Update other fields only if transaction is in draft status
        if transaction.status == 'draft':
            if 'description' in data:
                transaction.description = data['description']
            if 'type' in data:
                if data['type'] not in TRANSACTION_TYPES:
                    return jsonify({'error': f'Invalid transaction type: {data["type"]}'}), 400
                transaction.type = data['type']
            if 'transaction_date' in data:
                transaction.transaction_date = data['transaction_date']
            if 'notes' in data:
                transaction.notes = data['notes']
                
            # Update entries if provided
            if 'entries' in data:
                if not isinstance(data['entries'], list) or not data['entries']:
                    return jsonify({'error': 'At least one entry is required'}), 400
                    
                try:
                    entries = []
                    for entry_data in data['entries']:
                        entry = TransactionEntry(
                            account_id=entry_data.get('account_id'),
                            debit_amount=float(entry_data.get('debit_amount', 0)),
                            credit_amount=float(entry_data.get('credit_amount', 0)),
                            description=entry_data.get('description')
                        )
                        entries.append(entry)
                    
                    # Validate accounts before updating entries
                    Transaction._validate_accounts(user_id, entries)
                    transaction.entries = entries
                    
                except ValueError as e:
                    return jsonify({'error': f'Invalid entry data: {str(e)}'}), 400
        
        # Save changes
        transaction.modified_at = datetime.utcnow().isoformat()
        database.update_document(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            document_id=result['documents'][0]['$id'],
            data=transaction.to_dict(for_appwrite=True)
        )
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': transaction.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in update_transaction: {str(e)}")  # Debug print
        return jsonify({'error': f'Error updating transaction: {str(e)}'}), 500

@transactions_bp.route('/delete_transaction/<transaction_id>', methods=['DELETE'])
@require_auth
def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        database = Transaction.get_database()
        
        # Get transaction document
        result = database.list_documents(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            queries=[
                Query.equal('transaction_id', transaction_id),
                Query.equal('user_id', user_id)
            ]
        )
        
        if not result['documents']:
            return jsonify({'error': 'Transaction not found'}), 404
            
        transaction = Transaction.from_dict(result['documents'][0])
        
        # Verify transaction is in draft status
        if transaction.status != 'void':
            return jsonify({'error': 'Only void transactions can be deleted'}), 400
            
        # Delete the transaction
        database.delete_document(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            document_id=result['documents'][0]['$id']
        )
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error deleting transaction: {str(e)}'}), 500

@transactions_bp.route('/post_transaction/<transaction_id>', methods=['POST'])
@require_auth
def post_transaction(transaction_id: str):
    """Post a transaction - updates status to posted"""
    try:
        user_id = request.headers.get('X-Appwrite-User-ID')
        database = Transaction.get_database()
        
        # Query for transaction by transaction_id
        transactions = database.list_documents(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            queries=[
                Query.equal('transaction_id', transaction_id),
                Query.equal('user_id', user_id)
            ]
        )
        
        if not transactions.get('documents', []):
            return jsonify({'error': 'Transaction not found'}), 404
            
        transaction_doc = transactions['documents'][0]
        document_id = transaction_doc['$id']
        
        # Create transaction object and post it
        transaction = Transaction.from_dict(transaction_doc)
        transaction.post()  # This will validate status and update posted_at
        transaction.modified_at = datetime.utcnow().isoformat()
        
        # Update in database using proper serialization
        update_data = transaction.to_dict(for_appwrite=True)
        # Remove any Appwrite system fields
        appwrite_fields = ['$id', '$createdAt', '$updatedAt', '$permissions', '$collectionId', '$databaseId']
        update_data = {k: v for k, v in update_data.items() if k not in appwrite_fields}
        
        updated_doc = database.update_document(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            document_id=document_id,
            data=update_data
        )
        
        return jsonify({
            'message': 'Transaction posted successfully',
            'transaction': transaction.to_dict()  # Return normal dict for API response
        }), 200
        
    except ValueError as e:
        # Handle validation errors from post() method
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in post_transaction: {str(e)}")  # Debug print
        return jsonify({'error': f'Error posting transaction: {str(e)}'}), 500

@transactions_bp.route('/void_transaction/<transaction_id>', methods=['POST'])
@require_auth
def void_transaction(transaction_id: str):
    """Void a transaction - updates status to voided"""
    try:
        data = request.json
        if not data or 'void_reason' not in data:
            return jsonify({'error': 'Void reason is required'}), 400
            
        database = Transaction.get_database()
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        # Query for transaction by transaction_id
        transactions = database.list_documents(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            queries=[
                Query.equal('transaction_id', transaction_id),
                Query.equal('user_id', user_id)
            ]
        )
        
        if not transactions.get('documents', []):
            return jsonify({'error': 'Transaction not found'}), 404
            
        transaction_doc = transactions['documents'][0]
        document_id = transaction_doc['$id']
        
        # Create transaction object and void it
        transaction = Transaction.from_dict(transaction_doc)
        transaction.void(data['void_reason'])
        
        # Update in database using proper serialization
        update_data = transaction.to_dict(for_appwrite=True)
        # Remove any Appwrite system fields
        appwrite_fields = ['$id', '$createdAt', '$updatedAt', '$permissions', '$collectionId', '$databaseId']
        update_data = {k: v for k, v in update_data.items() if k not in appwrite_fields}
        
        updated_doc = database.update_document(
            database_id=Transaction.DATABASE_ID,
            collection_id=Transaction.COLLECTION_ID,
            document_id=document_id,
            data=update_data
        )
        
        return jsonify({
            'message': 'Transaction voided successfully',
            'transaction': transaction.to_dict()
        }), 200
        
    except ValueError as e:
        # Handle validation errors from void() method
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in void_transaction: {str(e)}")
        return jsonify({'error': f'Error voiding transaction: {str(e)}'}), 500
