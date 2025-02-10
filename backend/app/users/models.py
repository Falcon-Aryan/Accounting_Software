from datetime import datetime
import os
from typing import Optional, Dict, List, Any

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.services.account import Account
from appwrite.id import ID
from appwrite.query import Query

class User:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "users"

    def __init__(self, user_id: str, email: str, name: str,
                 phone: str,
                 company_name: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.phone = phone
        self.company_name = company_name
        self.created_at = created_at or datetime.now()

    @classmethod
    def create_user(cls, email: str, password: str, name: str, 
                   phone: str,
                   company_name: Optional[str] = None) -> 'User':
        # Initialize Appwrite client
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))

        # Create user account
        users = Users(client)
        user = users.create(
            user_id=ID.unique(),
            email=email,
            password=password,
            name=name
        )

        # Store additional user data in database
        databases = Databases(client)
        user_data = {
            'user_id': user['$id'],
            'email': email,
            'name': name,
            'phone': phone,
            'company_name': company_name,
            'created_at': datetime.now().isoformat()
        }
        
        databases.create_document(
            database_id=cls.DATABASE_ID,
            collection_id=cls.COLLECTION_ID,
            document_id=user['$id'],
            data=user_data
        )

        return cls(
            user_id=user['$id'],
            email=email,
            name=name,
            phone=phone,
            company_name=company_name
        )

    @classmethod
    def get_user(cls, user_id: str) -> Optional['User']:
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))

        databases = Databases(client)
        try:
            doc = databases.get_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=user_id
            )
            return cls(
                user_id=doc['user_id'],
                email=doc['email'],
                name=doc['name'],
                phone=doc['phone'],
                company_name=doc.get('company_name'),
                created_at=datetime.fromisoformat(doc['created_at'])
            )
        except:
            return None

    @classmethod
    def get_current_user(cls, session_id: str) -> Optional['User']:
        """Get the current user from a session ID"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_session(session_id)  # Set the session
        
        try:
            # Get current user's account
            account = Account(client)
            user = account.get()
            
            # Return user object
            return cls.get_user(user['$id'])
        except:
            return None
            
    @classmethod
    def validate_session(cls, session_id: str) -> bool:
        """Validate if a session ID is valid"""
        user = cls.get_current_user(session_id)
        return user is not None

    @classmethod
    def get_all_users(cls) -> List['User']:
        """Get all users from the database"""
        # Initialize Appwrite client
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))

        # Get users from database
        databases = Databases(client)
        try:
            result = databases.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID
            )
            
            users = []
            for doc in result['documents']:
                user = cls(
                    user_id=doc['user_id'],
                    email=doc['email'],
                    name=doc['name'],
                    phone=doc.get('phone', ''),
                    company_name=doc.get('company_name'),
                    created_at=datetime.fromisoformat(doc['created_at']) if 'created_at' in doc else None
                )
                users.append(user)
            
            return users
            
        except Exception as e:
            raise Exception(f"Failed to get users: {str(e)}")

    @classmethod
    def delete_user(cls, user_id: str) -> Dict[str, Any]:
        """Delete a user and all associated data"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        users = Users(client)
        
        results = {
            'user_deleted': False,
            'database_cleaned': False,
            'errors': []
        }
        
        try:
            # First sync database with auth to clean up all data
            sync_results = cls.sync_database_with_auth(user_id)
            results['database_cleaned'] = sync_results['action'] == 'delete'
            if sync_results['errors']:
                results['errors'].extend(sync_results['errors'])
            
            # Then delete the user from Auth
            try:
                users.delete(user_id)
                results['user_deleted'] = True
            except Exception as e:
                if "User with the requested ID could not be found" in str(e):
                    # User already deleted from Auth, consider this a success
                    results['user_deleted'] = True
                else:
                    results['errors'].append(f"Error deleting user from Auth: {str(e)}")
            
            return results
            
        except Exception as e:
            results['errors'].append(f"Unexpected error: {str(e)}")
            return results

    @classmethod
    def sync_database_with_auth(cls, user_id: str, force_cleanup: bool = False) -> Dict[str, Any]:
        """Synchronize database with Auth for a given user_id.
        If user exists in Auth but not in database, creates necessary records.
        If user doesn't exist in Auth but exists in database, purges all records.
        If force_cleanup is True, will delete all data for this user_id regardless of Auth state."""
        
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        databases = Databases(client)
        users = Users(client)
        
        results = {
            'action': None,  # 'create' or 'delete'
            'user_exists_in_auth': False,
            'user_exists_in_db': False,
            'records_created': {},
            'records_deleted': {},
            'errors': []
        }
        
        try:
            # Check if user exists in Auth
            try:
                auth_user = users.get(user_id)
                results['user_exists_in_auth'] = True
            except Exception:
                auth_user = None
            
            # Case 1: Force cleanup requested
            if force_cleanup:
                results['action'] = 'delete'
                collections_to_clean = [
                    ('accounts', 'chart_of_accounts'),
                    ('transactions', 'transactions'),
                    ('invoices', 'invoices'),
                    ('estimates', 'estimates'),
                    ('products', 'products'),
                    ('services', 'services'),
                    ('customers', 'customers'),
                    ('users', 'users')
                ]
                
                for collection_name, collection_id in collections_to_clean:
                    try:
                        while True:  # Handle pagination
                            docs = databases.list_documents(
                                database_id=cls.DATABASE_ID,
                                collection_id=collection_id,
                                queries=[
                                    Query.equal('user_id', user_id),
                                    Query.limit(100)  # Process in batches
                                ]
                            )
                            
                            if not docs['documents']:
                                break
                                
                            # Delete each document
                            deleted_count = 0
                            for doc in docs['documents']:
                                try:
                                    databases.delete_document(
                                        database_id=cls.DATABASE_ID,
                                        collection_id=collection_id,
                                        document_id=doc['$id']
                                    )
                                    deleted_count += 1
                                except Exception as e:
                                    results['errors'].append(f"Error deleting {collection_name} document {doc['$id']}: {str(e)}")
                            
                            results['records_deleted'][collection_name] = deleted_count
                            
                            if len(docs['documents']) < 100:  # No more documents to process
                                break
                            
                    except Exception as e:
                        results['errors'].append(f"Error cleaning {collection_name}: {str(e)}")
                
                return results
            
            # Check if user exists in database
            try:
                user_docs = databases.list_documents(
                    database_id=cls.DATABASE_ID,
                    collection_id=cls.COLLECTION_ID,
                    queries=[Query.equal('user_id', user_id)]
                )
                results['user_exists_in_db'] = len(user_docs['documents']) > 0
            except Exception as e:
                results['errors'].append(f"Error checking database: {str(e)}")
                return results
            
            # Case 1: User exists in Auth but not in database
            if auth_user and not results['user_exists_in_db']:
                results['action'] = 'create'
                try:
                    # Create user document
                    user_data = {
                        'user_id': auth_user['$id'],
                        'email': auth_user['email'],
                        'name': auth_user.get('name', ''),
                        'created_at': auth_user['$createdAt']
                    }
                    databases.create_document(
                        database_id=cls.DATABASE_ID,
                        collection_id=cls.COLLECTION_ID,
                        document_id=ID.unique(),
                        data=user_data
                    )
                    results['records_created']['user'] = True
                    
                    # Create default accounts
                    from ..chart_of_accounts.models import Account
                    Account.create_default_accounts(user_id)
                    results['records_created']['accounts'] = True
                    
                except Exception as e:
                    results['errors'].append(f"Error creating records: {str(e)}")
            
            # Case 2: User doesn't exist in Auth but exists in database
            elif not auth_user and results['user_exists_in_db']:
                results['action'] = 'delete'
                collections_to_clean = [
                    ('accounts', 'chart_of_accounts'),
                    ('transactions', 'transactions'),
                    ('invoices', 'invoices'),
                    ('estimates', 'estimates'),
                    ('products', 'products'),
                    ('services', 'services'),
                    ('customers', 'customers'),
                    ('users', 'users')
                ]
                
                for collection_name, collection_id in collections_to_clean:
                    try:
                        # Get all documents for this user
                        docs = databases.list_documents(
                            database_id=cls.DATABASE_ID,
                            collection_id=collection_id,
                            queries=[Query.equal('user_id', user_id)]
                        )
                        
                        # Delete each document
                        deleted_count = 0
                        for doc in docs['documents']:
                            try:
                                databases.delete_document(
                                    database_id=cls.DATABASE_ID,
                                    collection_id=collection_id,
                                    document_id=doc['$id']
                                )
                                deleted_count += 1
                            except Exception as e:
                                results['errors'].append(f"Error deleting {collection_name} document {doc['$id']}: {str(e)}")
                        
                        results['records_deleted'][collection_name] = deleted_count
                        
                    except Exception as e:
                        results['errors'].append(f"Error cleaning {collection_name}: {str(e)}")
            
            return results
            
        except Exception as e:
            results['errors'].append(f"Unexpected error: {str(e)}")
            return results

    @classmethod
    def bulk_sync_database_with_auth(cls) -> Dict[str, Any]:
        """Synchronize all users between Auth and Database"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        users = Users(client)
        databases = Databases(client)
        
        results = {
            'total_users_processed': 0,
            'users_created': 0,
            'users_cleaned': 0,
            'errors': [],
            'details': {}
        }
        
        try:
            # Step 1: Get all users from Auth
            auth_users = {}
            offset = 0
            while True:
                user_list = users.list(queries=[Query.limit(100), Query.offset(offset)])
                if not user_list['users']:
                    break
                    
                for user in user_list['users']:
                    auth_users[user['$id']] = user
                
                offset += len(user_list['users'])
                if len(user_list['users']) < 100:
                    break
            
            # Step 2: Get all users from database
            db_users = set()
            offset = 0
            while True:
                db_list = databases.list_documents(
                    database_id=cls.DATABASE_ID,
                    collection_id=cls.COLLECTION_ID,
                    queries=[Query.limit(100), Query.offset(offset)]
                )
                
                if not db_list['documents']:
                    break
                    
                for doc in db_list['documents']:
                    db_users.add(doc['user_id'])
                
                offset += len(db_list['documents'])
                if len(db_list['documents']) < 100:
                    break
            
            # Step 3: Process each Auth user
            for user_id in auth_users:
                try:
                    sync_result = cls.sync_database_with_auth(user_id)
                    results['details'][user_id] = sync_result
                    results['total_users_processed'] += 1
                    
                    if sync_result['action'] == 'create':
                        results['users_created'] += 1
                except Exception as e:
                    results['errors'].append(f"Error processing Auth user {user_id}: {str(e)}")
            
            # Step 4: Clean up database users not in Auth
            for user_id in db_users:
                if user_id not in auth_users:
                    try:
                        sync_result = cls.sync_database_with_auth(user_id, force_cleanup=True)
                        results['details'][user_id] = sync_result
                        results['total_users_processed'] += 1
                        results['users_cleaned'] += 1
                    except Exception as e:
                        results['errors'].append(f"Error cleaning database user {user_id}: {str(e)}")
            
            return results
            
        except Exception as e:
            results['errors'].append(f"Unexpected error during bulk sync: {str(e)}")
            return results