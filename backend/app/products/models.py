from datetime import datetime
import os
import random
import hashlib
from typing import Dict, List, Optional

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID

class Product:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = 'products'  # physical products collection
    
    def __init__(self, product_id: str, user_id: str, name: str, price: float,
                 stock: int, sku: str, description: Optional[str] = None,
                 category: Optional[List[str]] = None, created_at: Optional[str] = None,
                 updated_at: Optional[str] = None):
        self.product_id = product_id
        self.user_id = user_id
        self.name = name
        self.price = price
        self.stock = stock
        self.sku = sku
        self.description = description
        self.category = category or []  # Initialize as empty list if None
        self.type = 'product'  # Always set to 'product'
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'product_id': self.product_id,
            'user_id': self.user_id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'sku': self.sku,
            'description': self.description,
            'category': self.category,
            'type': self.type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Product':
        return Product(
            product_id=data['product_id'],
            user_id=data['user_id'],
            name=data['name'],
            price=data['price'],
            stock=data['stock'],
            sku=data['sku'],
            description=data.get('description'),
            category=data.get('category', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @staticmethod
    def generate_product_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"PROD{first_half}-{second_half}"
            return id
    
    @staticmethod
    def generate_sku(user_id: str) -> str:
        """Generate a unique SKU for a product
        
        Format: SKU-{user_hash}-{first_6_digits}-{last_6_digits}
        - user_hash: First 4 chars of SHA-256 hash of user_id
        - first_6_digits: First 6 random digits
        - last_6_digits: Last 6 random digits
        """
        
        # Generate a 4-character hash of the user_id
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:4]
        
        # Generate two groups of 6 random digits
        first_half = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        second_half = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Combine to form SKU with dashes
        return f"SKU-{user_hash}-{first_half}-{second_half}"
    
    @classmethod
    def get_database(cls) -> Databases:
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)
    
    @classmethod
    def create_product(cls, user_id: str, name: str, price: float, stock: int,
                      sku: Optional[str] = None, description: Optional[str] = None,
                      category: Optional[List[str]] = None) -> 'Product':
        """Create a new physical product"""
        try:
            print(f"\nAttempting to create product:")
            print(f"name: {name}")
            
            # Generate SKU if not provided
            if not sku:
                sku = cls.generate_sku(user_id)
            print(f"sku: {sku}")
            
            # Check for existing product with same SKU
            existing = cls.check_existing_product(user_id, sku)
            if existing:
                raise Exception(f"Product with SKU {sku} already exists")
            
            database = cls.get_database()
            product_id = cls.generate_product_id()
            
            product_data = {
                'product_id': product_id,
                'user_id': user_id,
                'name': name,
                'price': price,
                'stock': stock,
                'sku': sku,
                'description': description,
                'category': category or [],
                'type': 'product',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = database.create_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=product_id,
                data=product_data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error creating product: {str(e)}")
            raise
    
    @classmethod
    def check_existing_product(cls, user_id: str, sku: str) -> Optional['Product']:
        """Check if a product with the given SKU already exists for this user"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.equal('sku', sku)
                ]
            )
            
            if result['documents']:
                return cls.from_dict(result['documents'][0])
            return None
            
        except Exception as e:
            print(f"Error checking existing product: {str(e)}")
            return None
    
    @classmethod
    def get_products_by_user(cls, user_id: str) -> List['Product']:
        """Get all products for a specific user"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            return [cls.from_dict(doc) for doc in result['documents']]
            
        except Exception as e:
            raise Exception(f"Error getting products: {str(e)}")
    
    @classmethod
    def get_product(cls, product_id: str, user_id: str = None) -> Optional['Product']:
        """Get a product by ID. If user_id is provided, verify ownership."""
        try:
            database = cls.get_database()
            result = database.get_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=product_id
            )
            
            product = cls.from_dict(result)
            
            # If user_id is provided, verify ownership
            if user_id and product.user_id != user_id:
                return None
                
            return product
            
        except Exception as e:
            print(f"Error getting product: {str(e)}")
            return None
    
    @classmethod
    def update_product(cls, product_id: str, user_id: str, data: Dict) -> Optional['Product']:
        """Update a product, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_product(product_id, user_id)
            if not existing:
                return None
            
            database = cls.get_database()
            
            # Ensure we don't modify critical fields
            data['user_id'] = user_id
            data['product_id'] = product_id
            data['updated_at'] = datetime.utcnow().isoformat()
            
            result = database.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=product_id,
                data=data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            return None
    
    @classmethod
    def delete_product(cls, product_id: str, user_id: str) -> bool:
        """Delete a product, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_product(product_id, user_id)
            if not existing:
                return False
            
            database = cls.get_database()
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=product_id
            )
            
            return True
            
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False
    
    @classmethod
    def get_products_by_category(cls, user_id: str, category: str) -> List['Product']:
        """Get all products that have the specified category"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.search('category', category)
                ]
            )
            
            return [cls.from_dict(doc) for doc in result['documents']]
            
        except Exception as e:
            print(f"Error getting products by category: {str(e)}")
            raise