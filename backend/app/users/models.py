from firebase_admin import auth
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class UserModel:
    USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users', 'users.json')
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

    @staticmethod
    def _format_timestamp(timestamp_ms: Optional[int]) -> Optional[str]:
        """Convert millisecond timestamp to ISO format date string"""
        if timestamp_ms is None:
            return None
        return datetime.fromtimestamp(timestamp_ms / 1000).isoformat()

    @staticmethod
    def _ensure_user_directory(uid: str) -> None:
        """Ensure user directory exists with necessary JSON files"""
        user_dir = os.path.join(UserModel.DATA_DIR, uid)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            
            # Load default accounts and other main JSON files
            default_accounts_path = os.path.join(UserModel.DATA_DIR, 'default_accounts.json')
            company_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'company.json')
            advanced_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'advanced.json')
            invoices_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'invoices.json')
            customers_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'customers.json')
            products_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'products.json')
            estimates_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'estimates.json')
            transactions_path = os.path.join(UserModel.DATA_DIR, 'defaults', 'transactions.json')
            
            # Load all main JSON files
            with open(default_accounts_path, 'r') as f:
                default_accounts = json.load(f)
            with open(company_path, 'r') as f:
                company_data = json.load(f)
            with open(advanced_path, 'r') as f:
                advanced_data = json.load(f)
            with open(invoices_path, 'r') as f:
                invoices_data = json.load(f)
            with open(customers_path, 'r') as f:
                customers_data = json.load(f)
            with open(products_path, 'r') as f:
                products_data = json.load(f)
            with open(estimates_path, 'r') as f:
                estimates_data = json.load(f)
            with open(transactions_path, 'r') as f:
                transactions_data = json.load(f)
            
            # Update timestamps in the loaded data
            current_time = datetime.now().isoformat()
            
            # Define directory structure with initial JSON content
            structure = {
                'invoices': {
                    'filename': 'invoices.json',
                    'content': {
                        **invoices_data,
                        'metadata': {
                            **invoices_data.get('metadata', {}),
                            'lastUpdated': current_time
                        }
                    }
                },
                'customers': {
                    'filename': 'customers.json',
                    'content': {
                        **customers_data,
                        'metadata': {
                            **customers_data.get('metadata', {}),
                            'lastUpdated': current_time
                        }
                    }
                },
                'products': {
                    'filename': 'products.json',
                    'content': {
                        **products_data,
                        'metadata': {
                            **products_data.get('metadata', {}),
                            'lastUpdated': current_time
                        }
                    }
                },
                'estimates': {
                    'filename': 'estimates.json',
                    'content': {
                        **estimates_data,
                        'metadata': {
                            **estimates_data.get('metadata', {}),
                            'lastUpdated': current_time
                        }
                    }
                },
                'company': {
                    'filename': 'company.json',
                    'content': {
                        **company_data,
                        'metadata': {
                            **company_data.get('metadata', {}),
                            'lastUpdated': current_time,
                            'createdAt': current_time
                        }
                    }
                },
                'advanced': {
                    'filename': 'advanced.json',
                    'content': {
                        **advanced_data,
                        'metadata': {
                            **advanced_data.get('metadata', {}),
                            'lastUpdated': current_time
                        }
                    }
                },
                'transactions': {
                    'filename': 'transactions.json',
                    'content': {
                        **transactions_data,
                        'metadata': {
                            **transactions_data.get('metadata', {}),
                            'lastUpdated': current_time
                        }
                    }
                },
                'chart_of_accounts': {
                    'filename': 'chart_of_accounts.json',
                    'content': {
                        'accounts': default_accounts['accounts'],
                        'metadata': {
                            'lastUpdated': current_time,
                            'fiscalYear': datetime.now().year
                        },
                        'summary': default_accounts['summary']
                    }
                }
            }
            
            # Create each directory and its JSON file
            for dir_name, config in structure.items():
                dir_path = os.path.join(user_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                
                # Create JSON file
                file_path = os.path.join(dir_path, config['filename'])
                with open(file_path, 'w') as f:
                    json.dump(config['content'], f, indent=2)

    @staticmethod
    def create_user(email: str, password: str) -> Dict:
        """Create a new user in Firebase"""
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            
            # Format the user data
            user_data = {
                'uid': user.uid,
                'email': user.email,
                'createdAt': UserModel._format_timestamp(user.user_metadata.creation_timestamp),
                'lastLogin': UserModel._format_timestamp(user.user_metadata.last_sign_in_timestamp)
            }
            
            # Create user directory
            UserModel._ensure_user_directory(user.uid)
            
            return user_data
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    @staticmethod
    def sync_all_firebase_users() -> List[Dict]:
        """Sync all Firebase users with our users.json"""
        try:
            # Get all users from Firebase
            page = auth.list_users()
            users_list = []
            
            # Read existing users data
            users_data = UserModel._read_users_file()
            
            # Create a set of current Firebase UIDs
            firebase_uids = set()
            
            # First pass: Add or update users from Firebase
            for firebase_user in page.users:
                firebase_uids.add(firebase_user.uid)
                
                # Get existing user data to preserve additional fields
                existing_user = users_data['users'].get(firebase_user.uid, {})
                
                # Update only Firebase data, preserve everything else
                existing_user.update({
                    'uid': firebase_user.uid,
                    'email': firebase_user.email,
                    'createdAt': UserModel._format_timestamp(firebase_user.user_metadata.creation_timestamp),
                    'lastLogin': UserModel._format_timestamp(firebase_user.user_metadata.last_sign_in_timestamp)
                })
                
                users_data['users'][firebase_user.uid] = existing_user
                users_list.append(existing_user)
                
                # Ensure user directory exists with necessary files
                UserModel._ensure_user_directory(firebase_user.uid)
            
            # Second pass: Remove users that no longer exist in Firebase
            users_to_remove = set(users_data['users'].keys()) - firebase_uids
            for uid in users_to_remove:
                # Remove from users.json
                del users_data['users'][uid]
                
                # Remove their data directory if it exists
                user_dir = os.path.join(UserModel.DATA_DIR, uid)
                if os.path.exists(user_dir):
                    import shutil
                    shutil.rmtree(user_dir)
            
            # Write updated users data to file
            UserModel._write_users_file(users_data)
            
            return users_list
            
        except Exception as e:
            raise Exception(f"Error syncing users: {str(e)}")

    @staticmethod
    def sync_firebase_user(uid: str) -> Dict:
        """Sync a single Firebase user with our users.json"""
        try:
            # Get user from Firebase
            firebase_user = auth.get_user(uid)
            
            # Read current users
            users_data = UserModel._read_users_file()
            
            # Get existing user data to preserve additional fields
            existing_user = users_data['users'].get(uid, {})
            
            # Update Firebase data while preserving additional fields
            existing_user.update({
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'createdAt': UserModel._format_timestamp(firebase_user.user_metadata.creation_timestamp),
                'lastLogin': UserModel._format_timestamp(firebase_user.user_metadata.last_sign_in_timestamp)
            })
            
            # Update or add user
            users_data['users'][uid] = existing_user
            
            # Write back to file
            UserModel._write_users_file(users_data)
            
            # Ensure user directory exists
            UserModel._ensure_user_directory(uid)
            
            return existing_user
            
        except Exception as e:
            raise Exception(f"Error syncing user: {str(e)}")

    @staticmethod
    def get_all_users() -> List[Dict]:
        """Get all users from Firebase"""
        try:
            page = auth.list_users()
            users = []
            
            for user in page.users:
                users.append({
                    'uid': user.uid,
                    'email': user.email,
                    'createdAt': UserModel._format_timestamp(user.user_metadata.creation_timestamp),
                    'lastLogin': UserModel._format_timestamp(user.user_metadata.last_sign_in_timestamp)
                })
                
            return users
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")

    @staticmethod
    def update_user_profile(uid: str, data: Dict) -> Dict:
        """Update user profile in users.json"""
        try:
            # Read current data
            users_data = UserModel._read_users_file()
            
            if uid not in users_data['users']:
                raise Exception("User not found")
            
            user_data = users_data['users'][uid]
            
            # Initialize companyInfo if it doesn't exist
            if 'companyInfo' not in user_data:
                user_data['companyInfo'] = {}
            
            # Update allowed fields
            allowed_fields = ['firstName', 'lastName', 'phone', 'companyInfo']
            for field in allowed_fields:
                if field in data:
                    if field == 'companyInfo':
                        # Deep update companyInfo
                        user_data['companyInfo'].update(data['companyInfo'])
                    else:
                        user_data[field] = data[field]
            
            # Save changes
            UserModel._write_users_file(users_data)
            
            return user_data
            
        except Exception as e:
            raise Exception(f"Error updating user profile: {str(e)}")

    @staticmethod
    def delete_user(uid: str) -> bool:
        """Delete a user from Firebase and local storage"""
        try:
            # Delete from Firebase
            auth.delete_user(uid)
            
            # Delete from local storage
            users_data = UserModel._read_users_file()
            if uid in users_data['users']:
                del users_data['users'][uid]
                UserModel._write_users_file(users_data)
            
            # Delete user directory if it exists
            user_dir = os.path.join(UserModel.DATA_DIR, uid)
            if os.path.exists(user_dir):
                import shutil
                shutil.rmtree(user_dir)
            
            return True
        except auth.UserNotFoundError:
            return False
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")

    @staticmethod
    def _read_users_file() -> Dict:
        """Read the users.json file"""
        try:
            with open(UserModel.USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}}
        except Exception as e:
            raise Exception(f"Error reading users file: {str(e)}")

    @staticmethod
    def _write_users_file(data: Dict) -> None:
        """Write to the users.json file"""
        try:
            os.makedirs(os.path.dirname(UserModel.USERS_FILE), exist_ok=True)
            with open(UserModel.USERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise Exception(f"Error writing users file: {str(e)}")
