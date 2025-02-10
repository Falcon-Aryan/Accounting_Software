from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import json
import random

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query

from ..products.models import Product
from ..vendors.models import Vendor
from ..data_models.purchase_order_types import (
    PO_STATUSES,
    PO_STATUS_TRANSITIONS,
    PO_TYPES,
    PO_PAYMENT_TERMS,
    PO_LINE_ITEM_TYPES,
    PO_LINE_ITEM_STATUSES,
    PO_LINE_ITEM_STATUS_TRANSITIONS
)

@dataclass
class PurchaseOrderLineItem:
    """Line item for purchase orders"""
    line_item_type: str  # One of PO_LINE_ITEM_TYPES
    line_item_sku: str  # Product SKU (auto-generated if new product)
    line_item_name: str
    line_item_description: Optional[str]
    line_item_unit_cost: float  # Purchase price per unit
    line_item_quantity: float = 1.0
    line_item_received_quantity: float = 0.0
    line_item_status: str = 'pending'  # One of PO_LINE_ITEM_STATUSES
    line_item_expected_delivery_date: Optional[str] = None
    line_item_last_received_date: Optional[str] = None
    
    def __post_init__(self):
        """Validate line item data"""
        if self.line_item_type not in PO_LINE_ITEM_TYPES:
            raise ValueError(f"Invalid line item type. Must be one of: {', '.join(PO_LINE_ITEM_TYPES)}")
        if self.line_item_quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if self.line_item_unit_cost < 0:
            raise ValueError("Unit cost cannot be negative")
        if self.line_item_received_quantity < 0:
            raise ValueError("Received quantity cannot be negative")
        if self.line_item_received_quantity > self.line_item_quantity:
            raise ValueError("Received quantity cannot exceed ordered quantity")
        if self.line_item_status not in PO_LINE_ITEM_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(PO_LINE_ITEM_STATUSES)}")
            
    def update_status(self, new_status: str) -> None:
        """Update line item status with validation"""
        if new_status not in PO_LINE_ITEM_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(PO_LINE_ITEM_STATUSES)}")
            
        # Check if status transition is valid
        if new_status not in PO_LINE_ITEM_STATUS_TRANSITIONS[self.line_item_status]:
            raise ValueError(f"Invalid status transition from {self.line_item_status} to {new_status}")
            
        self.line_item_status = new_status
        
    def receive_quantity(self, quantity: float) -> None:
        """Record receipt of quantity"""
        if quantity <= 0:
            raise ValueError("Received quantity must be greater than 0")
            
        new_total = self.line_item_received_quantity + quantity
        if new_total > self.line_item_quantity:
            raise ValueError(f"Total received quantity ({new_total}) would exceed ordered quantity ({self.line_item_quantity})")
            
        self.line_item_received_quantity = new_total
        self.line_item_last_received_date = datetime.utcnow().isoformat()
        
        # Update status based on received quantity
        if self.line_item_received_quantity == self.line_item_quantity:
            self.update_status('received')
        elif self.line_item_received_quantity > 0:
            self.update_status('partially_received')
            
    def to_dict(self) -> Dict:
        """Convert line item to dictionary"""
        return {
            'type': self.line_item_type,
            'sku': self.line_item_sku,
            'name': self.line_item_name,
            'description': self.line_item_description,
            'unit_cost': self.line_item_unit_cost,
            'quantity': self.line_item_quantity,
            'received_quantity': self.line_item_received_quantity,
            'status': self.line_item_status,
            'expected_delivery_date': self.line_item_expected_delivery_date,
            'last_received_date': self.line_item_last_received_date
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'PurchaseOrderLineItem':
        """Create line item from dictionary"""
        return cls(
            line_item_type=data['type'],
            line_item_sku=data['sku'],
            line_item_name=data['name'],
            line_item_description=data.get('description'),
            line_item_unit_cost=float(data['unit_cost']),
            line_item_quantity=float(data['quantity']),
            line_item_received_quantity=float(data.get('received_quantity', 0.0)),
            line_item_status=data.get('status', 'pending'),
            line_item_expected_delivery_date=data.get('expected_delivery_date'),
            line_item_last_received_date=data.get('last_received_date')
        )

@dataclass
class PurchaseOrder:
    """Represents a Purchase Order in Appwrite"""
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "purchase_orders"
    
    user_id: str
    po_id: str = ""
    po_type: str = "standard"  # One of PO_TYPES
    po_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    due_date: str = field(default_factory=lambda: (datetime.utcnow() + timedelta(days=30)).isoformat())
    vendor_id: str = ""
    status: str = "draft"  # One of PO_STATUSES
    payment_terms: str = "net30"  # One of PO_PAYMENT_TERMS
    total: float = 0.0
    amount_paid: float = 0.0
    balance: float = 0.0
    line_items: List[PurchaseOrderLineItem] = field(default_factory=list)
    notes: Optional[str] = None
    document_id: Optional[str] = None
    sent_at: Optional[str] = None
    accepted_at: Optional[str] = None
    declined_at: Optional[str] = None
    decline_reason: Optional[str] = None
    received_at: Optional[str] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Initialize purchase order and validate data"""
        if self.status not in PO_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(PO_STATUSES)}")
        if self.po_type not in PO_TYPES:
            raise ValueError(f"Invalid PO type. Must be one of: {', '.join(PO_TYPES)}")
        if self.payment_terms not in PO_PAYMENT_TERMS:
            raise ValueError(f"Invalid payment terms. Must be one of: {', '.join(PO_PAYMENT_TERMS)}")
        self._calculate_total()
        self._calculate_balance()
        
    def _calculate_total(self):
        """Calculate total from line items"""
        self.total = sum(item.line_item_unit_cost * item.line_item_quantity for item in self.line_items)
        
    def _calculate_balance(self):
        """Calculate balance from total and amount_paid"""
        self.balance = self.total - self.amount_paid
        
    def update_status(self, new_status: str) -> None:
        """Update purchase order status with validation"""
        if new_status not in PO_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(PO_STATUSES)}")
            
        # Check if status transition is valid
        if new_status not in PO_STATUS_TRANSITIONS[self.status]:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
            
        # Update status and timestamp
        self.status = new_status
        timestamp = datetime.utcnow().isoformat()
        
        if new_status == 'sent':
            self.sent_at = timestamp
        elif new_status == 'accepted':
            self.accepted_at = timestamp
        elif new_status == 'declined':
            self.declined_at = timestamp
        elif new_status == 'received':
            self.received_at = timestamp
            
    def to_dict(self, for_appwrite: bool = False) -> Dict:
        """Convert purchase order to dictionary"""
        po_dict = {
            'user_id': self.user_id,
            'po_id': self.po_id,
            'po_type': self.po_type,
            'po_date': self.po_date,
            'due_date': self.due_date,
            'vendor_id': self.vendor_id,
            'status': self.status,
            'payment_terms': self.payment_terms,
            'total': self.total,
            'amount_paid': self.amount_paid,
            'balance': self.balance,
            'line_items': [item.to_dict() for item in self.line_items] if not for_appwrite else json.dumps([item.to_dict() for item in self.line_items]),
            'notes': self.notes,
            'sent_at': self.sent_at,
            'accepted_at': self.accepted_at,
            'declined_at': self.declined_at,
            'decline_reason': self.decline_reason,
            'received_at': self.received_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if not for_appwrite:
            po_dict['document_id'] = self.document_id
            
        return po_dict
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], document_id: Optional[str] = None) -> 'PurchaseOrder':
        """Create purchase order from dictionary"""
        # Convert line items from JSON string if needed
        line_items_data = data.get('line_items', '[]')
        if isinstance(line_items_data, str):
            line_items_data = json.loads(line_items_data)
            
        line_items = [PurchaseOrderLineItem.from_dict(item) for item in line_items_data]
        
        po = cls(
            user_id=data['user_id'],
            po_id=data['po_id'],
            po_type=data.get('po_type', 'standard'),
            po_date=data.get('po_date'),
            due_date=data.get('due_date'),
            vendor_id=data['vendor_id'],
            status=data.get('status', 'draft'),
            payment_terms=data.get('payment_terms', 'net30'),
            total=float(data.get('total', 0)),
            amount_paid=float(data.get('amount_paid', 0)),
            balance=float(data.get('balance', 0)),
            line_items=line_items,
            notes=data.get('notes'),
            sent_at=data.get('sent_at'),
            accepted_at=data.get('accepted_at'),
            declined_at=data.get('declined_at'),
            decline_reason=data.get('decline_reason'),
            received_at=data.get('received_at'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
        po.document_id = document_id
        return po
        
    @staticmethod
    def generate_po_id() -> str:
        """Generate a random PO ID with a specific format"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            po_id = f"PO{first_half}-{second_half}"
            return po_id
            
    @classmethod
    def validate_vendor(cls, user_id: str, vendor_id: str) -> Tuple[bool, Optional[str]]:
        """Validate that a vendor exists and belongs to the user
        
        Args:
            user_id: ID of the user
            vendor_id: ID of the vendor to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
            - is_valid: True if vendor is valid, False otherwise
            - error_message: None if valid, error message if invalid
        """
        try:
            if not vendor_id:
                return False, "Vendor ID is required"
                
            vendor = Vendor.get_vendor(vendor_id, user_id)
            if not vendor:
                return False, f"Vendor {vendor_id} not found or does not belong to user {user_id}"
                
            return True, None
            
        except Exception as e:
            return False, f"Error validating vendor: {str(e)}"
            
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
    def create_po(cls, user_id: str, vendor_id: str, line_items: List[PurchaseOrderLineItem],
                payment_terms: str = 'net30', notes: Optional[str] = None) -> 'PurchaseOrder':
        """Create a new purchase order"""
        try:
            # Validate vendor
            is_valid, error_message = cls.validate_vendor(user_id, vendor_id)
            if not is_valid:
                raise ValueError(error_message)
                
            # Create PO
            po = cls(
                user_id=user_id,
                vendor_id=vendor_id,
                line_items=line_items,
                payment_terms=payment_terms,
                notes=notes,
                po_id=cls.generate_po_id()
            )
            
            # Save to database
            database = cls.get_database()
            result = database.create_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=po.po_id,
                data=po.to_dict(for_appwrite=True)
            )
            
            return cls.from_dict(result, result['$id'])
            
        except Exception as e:
            raise Exception(f"Error creating purchase order: {str(e)}")
            
    @classmethod
    def get_database(cls):
        """Get Appwrite database instance"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)
        
    @classmethod
    def get_po_by_id(cls, po_id: str, user_id: str = None) -> Optional['PurchaseOrder']:
        """Get a purchase order by PO ID. If user_id is provided, verify ownership."""
        try:
            db = cls.get_database()
            result = db.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('po_id', po_id)]
            )
            
            if not result['documents']:
                raise Exception("Purchase order not found")
                
            po_doc = result['documents'][0]
            
            if user_id and po_doc['user_id'] != user_id:
                raise Exception("Unauthorized access to purchase order")
                
            return cls.from_dict(po_doc, po_doc['$id'])
            
        except Exception as e:
            raise Exception(f"Error getting purchase order: {str(e)}")
            
    @classmethod
    def get_pos_by_user(cls, user_id: str) -> List['PurchaseOrder']:
        """Get all purchase orders for a specific user"""
        try:
            db = cls.get_database()
            result = db.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            return [cls.from_dict(doc, doc['$id']) for doc in result['documents']]
            
        except Exception as e:
            raise Exception(f"Error getting purchase orders: {str(e)}")
            
    @classmethod
    def update_po(cls, po_id: str, user_id: str, data: Dict) -> Optional['PurchaseOrder']:
        """Update a purchase order, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_po_by_id(po_id, user_id)
            if not existing:
                return None
                
            # Don't allow updating certain fields
            protected_fields = ['user_id', 'po_id', 'created_at']
            for field in protected_fields:
                data.pop(field, None)
                
            data['updated_at'] = datetime.utcnow().isoformat()
            
            # Update line items if provided
            if 'line_items' in data and isinstance(data['line_items'], list):
                data['line_items'] = json.dumps(data['line_items'])
                
            db = cls.get_database()
            result = db.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=po_id,
                data=data
            )
            
            return cls.from_dict(result, result['$id'])
            
        except Exception as e:
            raise Exception(f"Error updating purchase order: {str(e)}")
            
    @classmethod
    def delete_po(cls, po_id: str, user_id: str) -> bool:
        """Delete a purchase order, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_po_by_id(po_id, user_id)
            if not existing:
                return False
                
            db = cls.get_database()
            db.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=po_id
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting purchase order: {str(e)}")