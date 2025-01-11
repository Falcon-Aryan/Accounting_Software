from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
import json
import random
from ..products.models import Product


ESTIMATE_STATUSES = [
    'draft',
    'sent',
    'accepted',
    'declined',
    'converted',
    'void'
]
PAYMENT_TERMS = ['due_on_receipt', 'net_15', 'net_30', 'net_60', 'custom']

@dataclass
class EstimateLineItem:
    """Represents a line item in an estimate"""
    product_id: str
    quantity: float = 1.0
    unit_price: float = 0.0
    description: str = ""
    total: float = 0.0

    def __post_init__(self):
        """Calculate total after initialization"""
        self.total = self.unit_price * self.quantity

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EstimateLineItem':
        """Create an EstimateLineItem instance from a dictionary"""
        return cls(
            product_id=data.get('product_id', ''),
            quantity=float(data.get('quantity', 1.0)),
            unit_price=float(data.get('unit_price', 0.0)),
            description=data.get('description', ''),
            total=float(data.get('total', 0.0))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert EstimateLineItem instance to dictionary"""
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'description': self.description,
            'total': self.total
        }

@dataclass
class Estimate:
    """Represents an Estimate entry"""
    id: str
    estimate_no: str 
    estimate_date: str  
    expiry_date: str  
    customer_name: str
    status: str
    line_items: List[EstimateLineItem] = field(default_factory=list)
    total_amount: float = 0.0
    payment_terms: str = 'due_on_receipt'  
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    customer_id: Optional[str] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None
    sent_at: Optional[str] = None
    accepted_at: Optional[str] = None  
    declined_at: Optional[str] = None  
    converted_at: Optional[str] = None  
    accepted_by: Optional[str] = None  
    declined_by: Optional[str] = None  
    decline_reason: Optional[str] = None  
    converted_to_invoice: Optional[Dict] = None  
    voided_at: Optional[str] = None
    void_reason: Optional[str] = None

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @staticmethod
    def get_user_data_file(uid: str) -> str:
        """Get the path to the user's estimates.json file"""
        return os.path.join(Estimate.BASE_DIR, 'data', uid, 'estimates.json')

    @staticmethod
    def generate_estimate_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(1000, 9999))
            second_half = str(random.randint(1000, 9999))
            id = f"{first_half}-{second_half}"
            return id

    def save(self, uid: str) -> None:
        """Save the estimate to the user's estimates.json file"""
        file_path = Estimate.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                data = {
                    "estimates": [], 
                    "summary": {
                        "total_count": 0,
                        "total_amount": 0.0
                    },
                    "metadata": {
                        "lastUpdated": datetime.utcnow().isoformat(),
                        "createdAt": datetime.utcnow().isoformat()
                    }
                }

            # Remove existing estimate if it exists
            data['estimates'] = [est for est in data['estimates'] if est['id'] != self.id]
            
            # Add updated estimate
            data['estimates'].append(self.to_dict())
            
            # Update summary
            data['summary']['total_count'] = len(data['estimates'])
            data['summary']['total_amount'] = sum(est['total_amount'] for est in data['estimates'])
            
            # Update metadata
            data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error saving estimate: {str(e)}")

    @staticmethod
    def get_all(uid: str) -> List['Estimate']:
        """Get all estimates"""
        try:
            file_path = Estimate.get_user_data_file(uid)
            if not os.path.exists(file_path):
                return []
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [Estimate.from_dict(estimate_data) for estimate_data in data.get('estimates', [])]
        except Exception as e:
            print(f"Error loading estimates: {str(e)}")
            return []

    @staticmethod
    def get_by_id(uid: str, id: str) -> Optional['Estimate']:
        """Get estimate by ID"""
        try:
            file_path = Estimate.get_user_data_file(uid)
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r') as f:
                data = json.load(f)
                estimate_data = next((est for est in data.get('estimates', []) if est['id'] == id), None)
                return Estimate.from_dict(estimate_data) if estimate_data else None
        except Exception as e:
            print(f"Error loading estimate: {str(e)}")
            return None



    def delete(self, uid: str) -> None:
        """Delete the estimate from the user's estimates.json file"""
        file_path = Estimate.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Remove the estimate
                data['estimates'] = [est for est in data['estimates'] if est['id'] != self.id]
                
                # Update summary
                data['summary']['total_count'] = len(data['estimates'])
                data['summary']['total_amount'] = sum(est['total_amount'] for est in data['estimates'])
                
                data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

                # Save the updated data
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error deleting estimate: {str(e)}")


    def __post_init__(self):
        """Calculate totals and set timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

        # Convert line_items from dict to EstimateLineItem objects
        if isinstance(self.line_items, list) and self.line_items and isinstance(self.line_items[0], dict):
            self.line_items = [EstimateLineItem(**item) for item in self.line_items]

        # Calculate total amount
        self.total_amount = sum(item.total for item in self.line_items)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Estimate':
        """Create an Estimate instance from a dictionary"""
        line_items = [EstimateLineItem.from_dict(item) for item in data.get('line_items', [])]
        
        return cls(
            id=data.get('id', ''),
            estimate_no=data.get('estimate_no', ''),
            estimate_date=data.get('estimate_date', ''),
            expiry_date=data.get('expiry_date', ''),
            customer_name=data.get('customer_name', ''),
            status=data.get('status', 'draft'),
            line_items=line_items,
            payment_terms=data.get('payment_terms', 'due_on_receipt'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            customer_id=data.get('customer_id'),
            notes=data.get('notes'),
            terms_conditions=data.get('terms_conditions'),
            sent_at=data.get('sent_at'),
            accepted_at=data.get('accepted_at'),
            declined_at=data.get('declined_at'),
            converted_at=data.get('converted_at'),
            accepted_by=data.get('accepted_by'),
            declined_by=data.get('declined_by'),
            decline_reason=data.get('decline_reason'),
            converted_to_invoice=data.get('converted_to_invoice'),
            voided_at=data.get('voided_at'),
            void_reason=data.get('void_reason')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Estimate instance to dictionary"""
        return {
            'id': self.id,
            'estimate_no': self.estimate_no,
            'estimate_date': self.estimate_date,
            'expiry_date': self.expiry_date,
            'customer_name': self.customer_name,
            'status': self.status,
            'line_items': [item.to_dict() for item in self.line_items],
            'total_amount': self.total_amount,
            'payment_terms': self.payment_terms,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'customer_id': self.customer_id,
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'sent_at': self.sent_at,
            'accepted_at': self.accepted_at,
            'declined_at': self.declined_at,
            'converted_at': self.converted_at,
            'accepted_by': self.accepted_by,
            'declined_by': self.declined_by,
            'decline_reason': self.decline_reason,
            'converted_to_invoice': self.converted_to_invoice,
            'voided_at': self.voided_at,
            'void_reason': self.void_reason
        }

    def mark_as_sent(self) -> None:
        """Mark estimate as sent"""
        if self.status != 'draft':
            raise ValueError("Only draft estimates can be marked as sent")
        self.status = 'sent'
        self.sent_at = datetime.utcnow().isoformat()

    def mark_as_accepted(self, accepted_by: Optional[str] = None) -> None:
        """Mark estimate as accepted"""
        if self.status != 'sent':
            raise ValueError("Only sent estimates can be accepted")
        self.status = 'accepted'
        self.accepted_at = datetime.utcnow().isoformat()
        self.accepted_by = accepted_by

    def mark_as_declined(self, declined_by: Optional[str] = None, reason: Optional[str] = None) -> None:
        """Mark estimate as declined"""
        if self.status != 'sent':
            raise ValueError("Only sent estimates can be declined")
        self.status = 'declined'
        self.declined_at = datetime.utcnow().isoformat()
        self.declined_by = declined_by
        self.decline_reason = reason

    def mark_as_converted(self, invoice_data: Dict[str, Any]) -> None:
        """Mark estimate as converted to invoice"""
        if self.status not in ['sent', 'accepted']:
            raise ValueError("Only sent or accepted estimates can be converted to invoice")
        self.status = 'converted'
        self.converted_at = datetime.utcnow().isoformat()
        self.converted_to_invoice = invoice_data

    def void(self, void_reason: Optional[str] = None) -> None:
        """Void the estimate"""
        if self.status in ['converted', 'void']:
            raise ValueError("Cannot void a converted or already voided estimate")
        self.status = 'void'
        self.voided_at = datetime.utcnow().isoformat()
        self.void_reason = void_reason

@dataclass
class EstimatesSummary:
    """Summary information about estimates"""
    total_count: int = 0
    total_amount: float = 0.0
    draft_count: int = 0
    sent_count: int = 0
    accepted_count: int = 0
    declined_count: int = 0
    converted_count: int = 0
    void_count: int = 0
    expired_count: int = 0
    draft_amount: float = 0.0
    sent_amount: float = 0.0
    accepted_amount: float = 0.0
    declined_amount: float = 0.0
    converted_amount: float = 0.0
    void_amount: float = 0.0
    expired_amount: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert EstimateSummary instance to dictionary"""
        return {
            'total_count': self.total_count,
            'total_amount': self.total_amount,
            'draft_count': self.draft_count,
            'sent_count': self.sent_count,
            'accepted_count': self.accepted_count,
            'declined_count': self.declined_count,
            'converted_count': self.converted_count,
            'void_count': self.void_count,
            'expired_count': self.expired_count,
            'draft_amount': self.draft_amount,
            'sent_amount': self.sent_amount,
            'accepted_amount': self.accepted_amount,
            'declined_amount': self.declined_amount,
            'converted_amount': self.converted_amount,
            'void_amount': self.void_amount,
            'expired_amount': self.expired_amount
        }
