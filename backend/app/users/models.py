from firebase_admin import auth
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class UserModel:
    USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users', 'users.json')

    @staticmethod
    def _read_users_file() -> Dict:
        """Read the users.json file"""
        try:
            print(f"Reading from file: {UserModel.USERS_FILE}")
            with open(UserModel.USERS_FILE, 'r') as f:
                data = json.load(f)
                print(f"Read data: {data}")
                return data
        except FileNotFoundError:
            print(f"File not found: {UserModel.USERS_FILE}")
            return {"users": {}}
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return {"users": {}}

    @staticmethod
    def _write_users_file(data: Dict) -> None:
        """Write to the users.json file"""
        try:
            print(f"Writing to file: {UserModel.USERS_FILE}")
            print(f"Data to write: {data}")
            os.makedirs(os.path.dirname(UserModel.USERS_FILE), exist_ok=True)
            with open(UserModel.USERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print("Write successful")
            # Verify the write
            with open(UserModel.USERS_FILE, 'r') as f:
                print(f"Verification - file contents after write: {f.read()}")
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            raise e

    @staticmethod
    def create_user(email: str, password: str) -> Dict:
        """Create a new user in Firebase"""
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            
            return {
                'uid': user.uid,
                'email': user.email,
                'createdAt': user.user_metadata.creation_timestamp,
                'lastLogin': user.user_metadata.last_sign_in_timestamp,
                'companyInfo': {
                    'name': '',
                    'address': '',
                    'phone': '',
                    'businessType': ''
                }
            }
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

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
                    'createdAt': user.user_metadata.creation_timestamp,
                    'lastLogin': user.user_metadata.last_sign_in_timestamp
                })
                
            return users
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")

    @staticmethod
    def get_user(uid: str) -> Optional[Dict]:
        """Get a specific user from Firebase"""
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'createdAt': user.user_metadata.creation_timestamp,
                'lastLogin': user.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise Exception(f"Error getting user: {str(e)}")

    @staticmethod
    def update_user(uid: str, data: Dict) -> Optional[Dict]:
        """Update a user in Firebase"""
        try:
            # Only update fields that are provided
            update_kwargs = {}
            if 'email' in data:
                update_kwargs['email'] = data['email']
            if 'password' in data:
                update_kwargs['password'] = data['password']

            user = auth.update_user(uid, **update_kwargs)
            
            return {
                'uid': user.uid,
                'email': user.email,
                'createdAt': user.user_metadata.creation_timestamp,
                'lastLogin': user.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")

    @staticmethod
    def delete_user(uid: str) -> bool:
        """Delete a user from Firebase"""
        try:
            auth.delete_user(uid)
            return True
        except auth.UserNotFoundError:
            return False
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")

    @staticmethod
    def sync_firebase_user(uid: str) -> Dict:
        """Sync a Firebase user with our users.json"""
        try:
            # Get user from Firebase
            firebase_user = auth.get_user(uid)
            
            # Prepare user data
            user_data = {
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'createdAt': firebase_user.user_metadata.creation_timestamp,
                'lastLogin': firebase_user.user_metadata.last_sign_in_timestamp,
                'companyInfo': {
                    'name': '',
                    'address': '',
                    'phone': '',
                    'businessType': ''
                }
            }

            # Read current users
            users_data = UserModel._read_users_file()
            
            # Update or add user
            users_data['users'][uid] = user_data
            
            # Write back to file
            UserModel._write_users_file(users_data)
            
            return user_data
            
        except Exception as e:
            raise Exception(f"Error syncing user: {str(e)}")

    @staticmethod
    def _format_timestamp(timestamp_ms: Optional[int]) -> Optional[str]:
        """Convert millisecond timestamp to ISO format date string"""
        if timestamp_ms is None:
            return None
        return datetime.fromtimestamp(timestamp_ms / 1000).isoformat()

    @staticmethod
    def sync_all_firebase_users() -> List[Dict]:
        """Sync all Firebase users with our users.json"""
        try:
            # Get all users from Firebase
            page = auth.list_users()
            users_list = []
            
            # Read existing users data
            users_data = UserModel._read_users_file()
            
            for firebase_user in page.users:
                user_data = {
                    'uid': firebase_user.uid,
                    'email': firebase_user.email,
                    'createdAt': UserModel._format_timestamp(firebase_user.user_metadata.creation_timestamp),
                    'lastLogin': UserModel._format_timestamp(firebase_user.user_metadata.last_sign_in_timestamp),
                    'companyInfo': users_data['users'].get(firebase_user.uid, {}).get('companyInfo', {
                        'name': '',
                        'address': '',
                        'phone': '',
                        'businessType': ''
                    })
                }
                users_data['users'][firebase_user.uid] = user_data
                users_list.append(user_data)
            
            # Write to file
            UserModel._write_users_file(users_data)
            
            return users_list
            
        except Exception as e:
            raise Exception(f"Error syncing users: {str(e)}")
