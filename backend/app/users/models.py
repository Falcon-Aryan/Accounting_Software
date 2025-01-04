from firebase_admin import auth
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class UserModel:
    USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users', 'users.json')

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
            
            # Create a set of current Firebase UIDs
            firebase_uids = set()
            
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
            
            # Remove users that no longer exist in Firebase
            users_to_remove = set(users_data['users'].keys()) - firebase_uids
            for uid in users_to_remove:
                del users_data['users'][uid]
            
            # Write to file
            UserModel._write_users_file(users_data)
            
            return users_list
            
        except Exception as e:
            raise Exception(f"Error syncing users: {str(e)}")

    @staticmethod
    def update_user_profile(uid: str, data: Dict) -> Dict:
        """Update user profile in users.json"""
        try:
            # Read current data
            users_data = UserModel._read_users_file()
            
            if uid not in users_data['users']:
                raise Exception("User not found")
            
            user_data = users_data['users'][uid]
            
            # Update allowed fields
            allowed_fields = ['firstName', 'lastName', 'phone', 'companyInfo']
            for field in allowed_fields:
                if field in data:
                    if field == 'companyInfo':
                        # Deep update companyInfo to preserve unspecified fields
                        user_data['companyInfo'].update(data['companyInfo'])
                    else:
                        user_data[field] = data[field]
            
            # Save changes
            UserModel._write_users_file(users_data)
            
            return user_data
            
        except Exception as e:
            raise Exception(f"Error updating user profile: {str(e)}")

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
