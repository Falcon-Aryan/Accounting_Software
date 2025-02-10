from flask import Blueprint, request, jsonify
import os
import sys
from appwrite.client import Client
from appwrite.services.account import Account as AppwriteAccount
from appwrite.services.users import Users

from appwrite.id import ID
from appwrite.input_file import InputFile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import User  # Import the User model
from ..auth.session_store import add_session, remove_session  # Import from session_store instead
from ..chart_of_accounts.models import Account as ChartAccount
from app.data_models.default_coa import DEFAULT_ACCOUNTS # Update import to include DEFAULT_ACCOUNTS

users_bp = Blueprint('users', __name__)

def init_admin_client():
    """Initialize Appwrite client with API key for admin operations"""
    client = Client()
    client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
    client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
    client.set_key(os.getenv('APPWRITE_API_KEY'))
    return client

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    try:
        # Validate required fields
        if not all(key in data for key in ['email', 'password', 'name']):
            return jsonify({
                'error': 'Missing required fields',
                'details': 'email, password, and name are required'
            }), 400
            
        # Create user using our User model
        try:
            user = User.create_user(
                email=data['email'],
                password=data['password'],
                name=data['name'],
                phone=data.get('phone', ''),  # Optional
                company_name=data.get('company_name')  # Optional
            )
            
            # Create default accounts for the new user
            try:
                default_accounts = ChartAccount.create_default_accounts(user.user_id)
                
                return jsonify({
                    'message': 'User created successfully with default accounts',
                    'user': {
                        'id': user.user_id,
                        'email': user.email,
                        'name': user.name,
                        'phone': user.phone,
                        'company_name': user.company_name,
                        'created_at': user.created_at.isoformat()
                    },
                    'default_accounts_created': len(default_accounts)
                }), 201
                
            except Exception as e:
                # If default accounts creation fails, still return success but with a warning
                return jsonify({
                    'message': 'User created successfully but default accounts creation failed',
                    'warning': str(e),
                    'user': {
                        'id': user.user_id,
                        'email': user.email,
                        'name': user.name,
                        'phone': user.phone,
                        'company_name': user.company_name,
                        'created_at': user.created_at.isoformat()
                    }
                }), 201
                
        except Exception as create_error:
            return jsonify({
                'error': 'Failed to create user',
                'details': str(create_error)
            }), 400
            
    except Exception as e:
        print(f"Registration Error: {str(e)}")  # Debug print
        return jsonify({
            'error': 'Server error',
            'details': str(e)
        }), 500

@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400

        # Use admin client for login
        client = init_admin_client()
        account = AppwriteAccount(client)  # Use renamed AppwriteAccount
        
        try:
            # First verify if user exists using Users API
            users = Users(client)
            user_list = users.list()
            user_exists = False
            user_data = None
            
            for user in user_list['users']:
                if user['email'] == email:
                    user_exists = True
                    user_data = user
                    break
            
            if not user_exists:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Create session
            session = account.create_email_password_session(email, password)
            
            add_session(session['$id'])

            return jsonify({
                'message': 'Login successful',
                'session': {
                    'id': session['$id'],
                    'userId': session['userId']
                },
                'user': {
                    'id': user_data['$id'],
                    'email': user_data['email'],
                    'name': user_data['name'],
                    'phone': user_data.get('phone', '')
                }
            }), 200
            
        except Exception as e:
            print(f"Appwrite Error: {str(e)}")  # Debug print
            return jsonify({'error': 'Invalid email or password', 'details': str(e)}), 401

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")  # Debug print
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@users_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Get session ID from headers
        session_id = request.headers.get('X-Appwrite-Session-ID')
        user_id = request.headers.get('X-Appwrite-User-ID')  # Also get user ID
        
        if not session_id or not user_id:
            return jsonify({'error': 'Session ID and User ID are required'}), 400
            
        # Initialize Appwrite client with API key for admin access
        client = init_admin_client()
        users = Users(client)
        
        try:
            # Delete the session using Users API
            users.delete_session(
                user_id=user_id,
                session_id=session_id
            )

            remove_session(session_id)

            return jsonify({
                'message': 'Logged out successfully'
            }), 200
            
        except Exception as auth_error:

            remove_session(session_id)
            return jsonify({
                'error': 'Failed to logout',
                'details': str(auth_error)
            }), 401
            
    except Exception as e:
        print(f"Logout Error: {str(e)}")  # Debug print
        return jsonify({
            'error': 'Server error',
            'details': str(e)
        }), 500


@users_bp.route('/create_default_accounts', methods=['POST'])
def create_default_accounts():
    """Create default accounts for existing users"""
    try:
        # Get all users
        users = User.get_all_users()
        results = {
            'success': [],
            'skipped': [],
            'failed': []
        }

        for user in users:
            try:
                # Get existing accounts for this user
                existing_accounts = ChartAccount.get_accounts_by_user(user.user_id)
                existing_account_numbers = {acc.account_number for acc in existing_accounts}
                
                # Filter out accounts that already exist
                accounts_to_create = [
                    acc for acc in DEFAULT_ACCOUNTS 
                    if acc['account_number'] not in existing_account_numbers
                ]
                
                if not accounts_to_create:
                    results['skipped'].append({
                        'user_id': user.user_id,
                        'email': user.email,
                        'reason': 'All default accounts already exist'
                    })
                    continue

                # Create missing default accounts
                created_accounts = []
                for account_data in accounts_to_create:
                    try:
                        account = ChartAccount.create_account(
                            user_id=user.user_id,
                            account_name=account_data["account_name"],
                            account_type=account_data["account_type"],
                            account_subtype=account_data["account_subtype"],
                            account_number=account_data["account_number"],
                            description=account_data["description"]
                        )
                        created_accounts.append(account)
                    except Exception as e:
                        print(f"Error creating account {account_data['account_name']} for user {user.email}: {str(e)}")
                        continue

                if created_accounts:
                    results['success'].append({
                        'user_id': user.user_id,
                        'email': user.email,
                        'accounts_created': len(created_accounts),
                        'accounts_already_existed': len(existing_accounts)
                    })
                else:
                    results['failed'].append({
                        'user_id': user.user_id,
                        'email': user.email,
                        'error': 'Failed to create any accounts'
                    })

            except Exception as e:
                results['failed'].append({
                    'user_id': user.user_id,
                    'email': user.email,
                    'error': str(e)
                })

        return jsonify({
            'message': 'Default accounts creation process completed',
            'summary': {
                'total_users': len(users),
                'successful_users': len(results['success']),
                'skipped_users': len(results['skipped']),
                'failed_users': len(results['failed'])
            },
            'details': results
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to process users',
            'details': str(e)
        }), 500


@users_bp.route('/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id: str):
    """Delete a user and all their associated data"""
    try:
        # Get user first to verify they exist and get email
        user = User.get_user(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'user_id': user_id
            }), 404

        # Delete user and all associated data
        results = User.delete_user(user_id)
        
        if results['user_deleted'] and results['database_cleaned']:
            return jsonify({
                'message': 'User and associated data deleted successfully',
                'details': {
                    'email': user.email,
                    'database_cleaned': True,
                    'errors': results['errors'] if results['errors'] else None
                }
            }), 200
        else:
            return jsonify({
                'error': 'User deletion partially failed',
                'details': results
            }), 500

    except Exception as e:
        return jsonify({
            'error': 'Failed to delete user',
            'details': str(e)
        }), 500

@users_bp.route('/sync/<user_id>', methods=['POST'])
def sync_user(user_id: str):
    """Synchronize user data between Auth and Database"""
    try:
        # Get force parameter from request
        force_cleanup = request.args.get('force', 'false').lower() == 'true'
        
        results = User.sync_database_with_auth(user_id, force_cleanup=force_cleanup)
        
        if not results['errors']:
            return jsonify({
                'message': f"Successfully {results['action']}d user data",
                'details': {
                    'action': results['action'],
                    'user_exists_in_auth': results['user_exists_in_auth'],
                    'user_exists_in_db': results['user_exists_in_db'],
                    'records_created': results['records_created'],
                    'records_deleted': results['records_deleted']
                }
            }), 200
        else:
            return jsonify({
                'error': 'Sync partially failed',
                'details': results
            }), 500

    except Exception as e:
        return jsonify({
            'error': 'Failed to sync user',
            'details': str(e)
        }), 500

@users_bp.route('/sync/bulk', methods=['POST'])
def bulk_sync():
    """Synchronize all users between Auth and Database"""
    try:
        results = User.bulk_sync_database_with_auth()
        
        if not results['errors']:
            return jsonify({
                'message': 'Successfully synchronized all users',
                'details': {
                    'total_users_processed': results['total_users_processed'],
                    'users_created': results['users_created'],
                    'users_cleaned': results['users_cleaned'],
                    'user_details': results['details']
                }
            }), 200
        else:
            return jsonify({
                'error': 'Bulk sync partially failed',
                'details': results
            }), 500

    except Exception as e:
        return jsonify({
            'error': 'Failed to perform bulk sync',
            'details': str(e)
        }), 500