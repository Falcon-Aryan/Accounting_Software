from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import random
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from ..customers.models import Customer
from ..products.models import Product
from ..services.models import Service

ESTIMATE_STATUSES = [
    'draft',
    'sent',
    'accepted',
    'declined',
    'expired',
    'converted'
]

PAYMENT_TERMS = [
    'net15',
    'net30',
    'net60',
    'due_on_receipt'
]

VALID_STATUS_TRANSITIONS = {
    'draft': ['sent', 'declined', 'expired'],
    'sent': ['accepted', 'declined', 'expired', 'draft'],
    'accepted': ['converted', 'draft'],
    'declined': ['draft'],
    'expired': ['draft'],
    'converted': ['draft']
}

@dataclass
class EstimateLineItem:
    """Line item for estimates"""
    type: str  # 'product' or 'service'
    item_id: str
    name: str
    price: float
    quantity: float = 1.0
    description: Optional[str] = None
    amount: float = 0.0

    def __post_init__(self):
        self.amount = self.quantity * self.price

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'type': self.type,
            'item_id': self.item_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description,
            'amount': self.amount
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EstimateLineItem':
        """Create from dictionary"""
        # Extract item_id and determine if it's a product or service
        item_id = data['item_id']
        quantity = float(data.get('quantity', 1.0))
        description = data.get('description')
        
        if item_id.startswith('PROD'):
            # Fetch product details
            product = Product.get_product(item_id)
            if not product:
                raise ValueError(f"Product not found: {item_id}")
            item_type = 'product'  # Infer type from ID
            name = product.name
            price = product.price
        elif item_id.startswith('SERV'):
            # Fetch service details
            service = Service.get_service(item_id)
            if not service:
                raise ValueError(f"Service not found: {item_id}")
            item_type = 'service'  # Infer type from ID
            name = service.name
            price = service.price
        else:
            raise ValueError(f"Invalid item_id format: {item_id}")
            
        return cls(
            type=item_type,
            item_id=item_id,
            name=name,
            price=price,
            quantity=quantity,
            description=description
        )

@dataclass
class Estimate:
    """Represents an Estimate in Appwrite"""
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "estimates"

    user_id: str
    estimate_id: str = ""
    estimate_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expiry_date: str = field(default_factory=lambda: (datetime.utcnow() + timedelta(days=30)).isoformat())
    customer_id: str = ""
    status: str = "draft"
    payment_terms: str = "net30"
    total: float = 0.0
    items: List[EstimateLineItem] = field(default_factory=list)
    notes: Optional[str] = None
    document_id: Optional[str] = None
    sent_at: Optional[str] = None
    accepted_at: Optional[str] = None
    declined_at: Optional[str] = None
    decline_reason: Optional[str] = None
    converted_at: Optional[str] = None

    def __post_init__(self):
        if self.status not in ESTIMATE_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(ESTIMATE_STATUSES)}")
        if self.payment_terms not in PAYMENT_TERMS:
            raise ValueError(f"Invalid payment terms. Must be one of: {', '.join(PAYMENT_TERMS)}")
        self._calculate_total()

    def _calculate_total(self):
        """Calculate total from items"""
        self.total = sum(item.amount for item in self.items)

    def to_dict(self, for_appwrite: bool = False) -> Dict[str, Any]:
        """Convert estimate to dictionary
        Args:
            for_appwrite (bool): If True, converts line_items to JSON string for Appwrite storage
        """
        # Convert line items to list of dicts or JSON string
        line_items = [item.to_dict() for item in self.items]
        line_items_data = json.dumps(line_items) if for_appwrite else line_items
        
        # Calculate total before creating dict
        self._calculate_total()
        
        # Include all fields regardless of value
        data = {
            'user_id': self.user_id,
            'estimate_id': self.estimate_id,
            'estimate_date': self.estimate_date,
            'expiry_date': self.expiry_date,
            'customer_id': self.customer_id,
            'status': self.status,
            'payment_terms': self.payment_terms,
            'total': self.total,
            'line_items': line_items_data,
            'notes': self.notes,
            # Make sure timestamps are included even if None
            'sent_at': self.sent_at if self.sent_at is not None else None,
            'accepted_at': self.accepted_at if self.accepted_at is not None else None,
            'declined_at': self.declined_at if self.declined_at is not None else None,
            'decline_reason': self.decline_reason if self.decline_reason is not None else None,
            'converted_at': self.converted_at if self.converted_at is not None else None
        }
        
        print(f"Debug - to_dict output: {data}")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any], document_id: Optional[str] = None) -> 'Estimate':
        """Create estimate from Appwrite document"""
        try:
            print(f"Debug - from_dict input: {data}")
            
            # Parse line items from JSON string if it's a string
            line_items_str = data.get('line_items', '[]')
            if isinstance(line_items_str, str):
                line_items_data = json.loads(line_items_str)
            else:
                line_items_data = line_items_str
                
            items = [EstimateLineItem.from_dict(item) for item in line_items_data]
            
            # Extract timestamps, ensuring they're properly handled
            sent_at = data.get('sent_at')
            accepted_at = data.get('accepted_at')
            declined_at = data.get('declined_at')
            converted_at = data.get('converted_at')
            
            print(f"Debug - Timestamps from data: sent_at={sent_at}, accepted_at={accepted_at}, declined_at={declined_at}, converted_at={converted_at}")
            
            estimate = cls(
                user_id=data['user_id'],
                estimate_id=data['estimate_id'],
                estimate_date=data['estimate_date'],
                expiry_date=data['expiry_date'],
                customer_id=data['customer_id'],
                status=data['status'],
                payment_terms=data['payment_terms'],
                notes=data.get('notes'),
                document_id=document_id,
                sent_at=sent_at,
                accepted_at=accepted_at,
                declined_at=declined_at,
                decline_reason=data.get('decline_reason'),
                converted_at=converted_at
            )
            
            # Set items and calculate total
            estimate.items = items
            estimate._calculate_total()
            
            print(f"Debug - Created estimate object with sent_at={estimate.sent_at}")
            return estimate
            
        except Exception as e:
            raise Exception(f"Error creating estimate from dict: {str(e)}")

    def check_expiration(self) -> bool:
        """Check if estimate has expired and update status if needed
        Returns:
            bool: True if estimate has expired, False otherwise
        """
        # Only check expiration for estimates in 'sent' status
        if self.status != 'sent':
            return False
            
        # Parse dates
        expiry_date = datetime.fromisoformat(self.expiry_date)
        current_time = datetime.utcnow()
        
        # Check if expired
        if current_time > expiry_date:
            self.update_status('expired')
            return True
            
        return False

    @staticmethod
    def generate_estimate_id() -> str:
        """Generate a random estimate ID with a specific format"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"EST{first_half}-{second_half}"
            return id

    @classmethod
    def validate_customer(cls, user_id: str, customer_id: str) -> bool:
        """Validate that a customer exists and belongs to the user"""
        try:
            customer = Customer.get_customer(customer_id, user_id)
            return customer is not None
        except Exception:
            return False

    @classmethod
    def validate_product(cls, user_id: str, product_id: str) -> bool:
        """Validate that a product exists and belongs to the user"""
        try:
            product = Product.get_product(product_id, user_id)
            return product is not None
        except Exception:
            return False

    @classmethod
    def validate_service(cls, user_id: str, service_id: str) -> bool:
        """Validate that a service exists and belongs to the user"""
        try:
            service = Service.get_service(service_id, user_id)
            return service is not None
        except Exception:
            return False

    @classmethod
    def create_estimate(cls, user_id: str, customer_id: str, items: List['EstimateLineItem'], payment_terms: str = 'net30'):
        """Create a new estimate"""
        # Validate customer
        if not cls.validate_customer(user_id, customer_id):
            raise ValueError(f"Customer {customer_id} not found or does not belong to user {user_id}")
            
        # Generate a unique estimate ID
        estimate_id = cls.generate_estimate_id()
        
        # Create the estimate instance
        estimate = cls(
            user_id=user_id,
            estimate_id=estimate_id,
            customer_id=customer_id,
            items=items,
            payment_terms=payment_terms
        )
        
        # Return the estimate object
        return estimate

    @classmethod
    def get_database(cls):
        """Get Appwrite database instance"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)

    @classmethod
    def get_estimate_by_id(cls, estimate_id: str, user_id: str = None):
        """Get an estimate by estimate ID. If user_id is provided, verify ownership."""
        try:
            db = cls.get_database()
            # Query by estimate_id instead of document_id
            result = db.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('estimate_id', estimate_id)]
            )
            
            if not result['documents']:
                raise Exception("Estimate not found")
                
            document = result['documents'][0]
            
            if user_id and document['user_id'] != user_id:
                raise Exception("Unauthorized access")
                
            # Pass the document ID when creating the estimate object
            return cls.from_dict(document, document_id=document['$id'])
            
        except Exception as e:
            raise Exception(f"Error getting estimate: {str(e)}")

    @classmethod
    def get_estimates_by_user(cls, user_id: str):
        """Get all estimates for a specific user"""
        try:
            db = cls.get_database()
            estimates = db.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            return [cls.from_dict(doc, doc['$id']) for doc in estimates['documents']]
            
        except Exception as e:
            raise Exception(f"Error getting estimates: {str(e)}")

    @classmethod
    def update_estimate(cls, estimate_id: str, user_id: str, data: Dict):
        """Update an estimate, verifying ownership first"""
        try:
            # Get existing estimate
            existing = cls.get_estimate_by_id(estimate_id, user_id)
            
            # Update the estimate with new data
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            
            # If updating status, validate it
            if 'status' in data and data['status'] not in ESTIMATE_STATUSES:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(ESTIMATE_STATUSES)}")
            
            # Update in database
            db = cls.get_database()
            estimate_doc = db.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=existing.document_id,  # Use the stored document_id for update
                data=existing.to_dict(for_appwrite=True)
            )
            
            return cls.from_dict(estimate_doc, estimate_doc['$id'])
            
        except Exception as e:
            raise Exception(f"Error updating estimate: {str(e)}")

    @classmethod
    def delete_estimate(cls, estimate_id: str, user_id: str):
        """Delete an estimate, verifying ownership first"""
        try:
            # Verify ownership and get document_id
            existing = cls.get_estimate_by_id(estimate_id, user_id)
            
            # Delete from database using document_id
            db = cls.get_database()
            db.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=existing.document_id
            )
            
        except Exception as e:
            raise Exception(f"Error deleting estimate: {str(e)}")

    def update_status(self, new_status: str, decline_reason: Optional[str] = None) -> None:
        """Update estimate status and set appropriate timestamps
        Args:
            new_status: New status to set
            decline_reason: Optional reason for decline status
        """
        if new_status not in ESTIMATE_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(ESTIMATE_STATUSES)}")
            
        if new_status not in VALID_STATUS_TRANSITIONS.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
            
        # Update status and relevant timestamps
        current_time = datetime.utcnow().isoformat()
        old_status = self.status
        self.status = new_status
        
        # Set timestamps based on status change
        if new_status == 'sent' and old_status != 'sent':
            self.sent_at = current_time
        elif new_status == 'accepted' and old_status != 'accepted':
            self.accepted_at = current_time
        elif new_status == 'declined' and old_status != 'declined':
            self.declined_at = current_time
            if decline_reason:
                self.decline_reason = decline_reason
        elif new_status == 'converted' and old_status != 'converted':
            self.converted_at = current_time