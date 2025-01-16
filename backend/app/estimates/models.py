from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import json
import random
from ..base.base_models import BaseDocument, LineItem
from ..products.models import Product
import traceback


ESTIMATE_STATUSES = [
    'draft',
    'pending',
    'accepted',
    'declined',
    'expired',
    'converted'
]
PAYMENT_TERMS = ['due_on_receipt', 'net_15', 'net_30', 'net_60', 'custom']

@dataclass
class Estimate(BaseDocument):
    """Represents an Estimate entry"""

    estimate_no: str = field(default_factory=lambda: f"EST-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000,9999)}")
    estimate_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expiry_date: str = field(default_factory=lambda: (datetime.utcnow() + timedelta(days=60)).isoformat())
    customer_name: str = ""
    sent_at: Optional[str] = None
    accepted_at: Optional[str] = None  
    declined_at: Optional[str] = None  
    decline_reason: Optional[str] = None
    converted_at: Optional[str] = None  
    converted_to_invoice: Optional[Dict] = None  

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def is_expired(self) -> bool:
        """Check if estimate has expired"""
        if self.status in ['converted', 'declined']:
            return False
        expiry_date = datetime.fromisoformat(self.expiry_date)
        return datetime.utcnow() > expiry_date

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
                        "draft_count": 0,
                        "pending_count": 0,
                        "accepted_count": 0,
                        "declined_count": 0,
                        "expired_count": 0,
                        "converted_count": 0,
                        "draft_amount": 0.0,
                        "pending_amount": 0.0,
                        "accepted_amount": 0.0,
                        "declined_amount": 0.0,
                        "expired_amount": 0.0,
                        "converted_amount": 0.0,
                        "total_converted": 0.0
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
            data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error saving estimate: {str(e)}")

    @staticmethod
    def get_all(uid: str) -> List['Estimate']:
        """Get all Estimates"""
        try:
            file_path = Estimate.get_user_data_file(uid)
            print(f"Looking for file at: {file_path}")

            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return []

            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Loaded data: {data}")
                estimates_data = data.get('estimates', [])
                print(f"Estimates data: {estimates_data}")
                
                estimates = []   
                for estimate_data in estimates_data:
                    try:
                        estimate = Estimate.from_dict(estimate_data)
                        if estimate.is_expired and estimate.status not in ['converted', 'declined']:
                            estimate.status = 'expired'
                            estimate.save(uid)
                        estimates.append(estimate)
                    except Exception as e:
                        print(f"Error converting estimate {estimate_data.get('id')}: {str(e)}")
                        continue
            
            print(f"Converted estimates: {estimates}")
            return estimates
        except Exception as e:
            print(f"Error loading estimates: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
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
                if estimate_data:
                    estimate = Estimate.from_dict(estimate_data)
                    # Check for expiry and update status if needed
                    if estimate.is_expired and estimate.status not in ['converted', 'declined']:
                        estimate.status = 'expired'
                        estimate.save(uid)
                    return estimate
                return None
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
                data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

                # Save the updated data
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error deleting estimate: {str(e)}")


    def __post_init__(self):
        """Calculate totals and set timestamps"""
        super().__post_init__()

        if isinstance(self.line_items, list) and self.line_items and isinstance(self.line_items[0], dict):
            self.line_items = [LineItem(**item) for item in self.line_items]

        self.total = sum(item.unit_price * item.quantity for item in self.line_items)

        # Set default status if not provided
        if not hasattr(self, 'status'):
            self.status = 'draft'

        # Validate status
        if self.status not in ESTIMATE_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {ESTIMATE_STATUSES}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Estimate':
        """Create an Estimate instance from a dictionary"""
        try:

            line_items = [LineItem.from_dict(item) if isinstance(item, dict) else item 
                        for item in data.get('line_items', [])]     

            estimate_data = {
                'id': data['id'],
                'customer_id': data['customer_id'],
                'estimate_no': data.get('estimate_no', ''),
                'estimate_date': data.get('estimate_date', ''),
                'expiry_date': data.get('expiry_date', ''),
                'customer_name': data.get('customer_name', ''),
                'line_items': line_items,
                'sent_at': data.get('sent_at'),
                'accepted_at': data.get('accepted_at'),
                'declined_at': data.get('declined_at'),
                'decline_reason': data.get('decline_reason'),
                'converted_at': data.get('converted_at'),
                'converted_to_invoice': data.get('converted_to_invoice'),
                'notes': data.get('notes', ''),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'status': data.get('status', 'draft'),
                'payment_terms': data.get('payment_terms', 'net_30'),
                'total': data.get('total', 0.0),
                'date': data.get('date', '')
            }
            
            return cls(**estimate_data)
        except Exception as e:
            print(f"Error in from_dict: {str(e)}")
            print(f"Data causing error: {data}")
            print(traceback.format_exc())
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert Estimate instance to dictionary"""
        base_dict = super().to_dict()
        estimate_dict = {
            'estimate_no': self.estimate_no,
            'estimate_date': self.estimate_date,
            'expiry_date': self.expiry_date,
            'customer_name': self.customer_name,
            'sent_at': self.sent_at,
            'accepted_at': self.accepted_at,
            'declined_at': self.declined_at,
            'decline_reason': self.decline_reason,
            'converted_at': self.converted_at,
            'converted_to_invoice': self.converted_to_invoice
        }
        result = {**base_dict, **estimate_dict}

        fields_to_remove = ['balance_due', 'payments', 'voided_at', 'void_reason']
        for field in fields_to_remove:
            result.pop(field, None)

        return result

@dataclass
class EstimatesSummary:
    """Summary information about estimates"""
    draft_count: int = 0
    pending_count: int = 0
    accepted_count: int = 0
    declined_count: int = 0
    expired_count: int = 0
    converted_count: int = 0
    draft_amount: float = 0.0
    pending_amount: float = 0.0
    accepted_amount: float = 0.0
    declined_amount: float = 0.0
    expired_amount: float = 0.0
    converted_amount: float = 0.0
    total_converted: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert EstimatesSummary instance to dictionary"""
        return {
            'draft_count': self.draft_count,
            'pending_count': self.pending_count,
            'accepted_count': self.accepted_count,
            'declined_count': self.declined_count,
            'expired_count': self.expired_count,
            'converted_count': self.converted_count,
            'draft_amount': self.draft_amount,
            'pending_amount': self.pending_amount,
            'accepted_amount': self.accepted_amount,
            'declined_amount': self.declined_amount,
            'expired_amount': self.expired_amount,
            'converted_amount': self.converted_amount,
            'total_converted': self.total_converted
        }