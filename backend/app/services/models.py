from datetime import datetime
import os
from typing import Dict, List, Optional
import random

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID

class Service:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = 'services'
    
    def __init__(self, service_id: str, user_id: str, name: str, price: float,
                 duration: Optional[str] = None, description: Optional[str] = None,
                 category: Optional[List[str]] = None, created_at: Optional[str] = None,
                 updated_at: Optional[str] = None):
        self.service_id = service_id
        self.user_id = user_id
        self.name = name
        self.price = price
        self.duration = duration
        self.description = description
        self.category = category or []  # Initialize as empty list if None
        self.type = 'service'
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'service_id': self.service_id,
            'user_id': self.user_id,
            'name': self.name,
            'price': self.price,
            'duration': self.duration,
            'description': self.description,
            'category': self.category,
            'type': self.type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Service':
        return Service(
            service_id=data['service_id'],
            user_id=data['user_id'],
            name=data['name'],
            price=data['price'],
            duration=data.get('duration'),
            description=data.get('description'),
            category=data.get('category', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @staticmethod
    def generate_service_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"SERV{first_half}-{second_half}"
            return id
    
    
    @classmethod
    def get_database(cls) -> Databases:
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)
    
    @classmethod
    def create_service(cls, user_id: str, name: str, price: float,
                      duration: Optional[str] = None, description: Optional[str] = None,
                      category: Optional[List[str]] = None) -> 'Service':
        """Create a new service"""
        try:
            print(f"\nAttempting to create service:")
            print(f"name: {name}")
            
            database = cls.get_database()
            service_id = cls.generate_service_id()
            
            service_data = {
                'service_id': service_id,
                'user_id': user_id,
                'name': name,
                'price': price,
                'duration': duration,
                'description': description,
                'category': category,
                'type': 'service',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = database.create_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=service_id,
                data=service_data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error creating service: {str(e)}")
            raise
    
    @classmethod
    def get_services_by_user(cls, user_id: str) -> List['Service']:
        """Get all services for a specific user"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            return [cls.from_dict(doc) for doc in result['documents']]
            
        except Exception as e:
            raise Exception(f"Error getting services: {str(e)}")
    
    @classmethod
    def get_services_by_category(cls, user_id: str, category: str) -> List['Service']:
        """Get all services that have the specified category"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.array_contains('category', category)
                ]
            )
            
            return [cls.from_dict(doc) for doc in result['documents']]
            
        except Exception as e:
            print(f"Error getting services by category: {str(e)}")
            return []
    
    @classmethod
    def get_service(cls, service_id: str, user_id: str = None) -> Optional['Service']:
        """Get a service by ID. If user_id is provided, verify ownership."""
        try:
            database = cls.get_database()
            result = database.get_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=service_id
            )
            
            service = cls.from_dict(result)
            
            # If user_id is provided, verify ownership
            if user_id and service.user_id != user_id:
                return None
                
            return service
            
        except Exception as e:
            print(f"Error getting service: {str(e)}")
            return None
    
    @classmethod
    def update_service(cls, service_id: str, user_id: str, data: Dict) -> Optional['Service']:
        """Update a service, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_service(service_id, user_id)
            if not existing:
                return None
            
            database = cls.get_database()
            
            # Ensure we don't modify critical fields
            data['user_id'] = user_id
            data['service_id'] = service_id
            data['type'] = 'service'
            data['updated_at'] = datetime.utcnow().isoformat()
            
            result = database.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=service_id,
                data=data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error updating service: {str(e)}")
            return None
    
    @classmethod
    def delete_service(cls, service_id: str, user_id: str) -> bool:
        """Delete a service, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_service(service_id, user_id)
            if not existing:
                return False
            
            database = cls.get_database()
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=service_id
            )
            
            return True
            
        except Exception as e:
            print(f"Error deleting service: {str(e)}")
            return False