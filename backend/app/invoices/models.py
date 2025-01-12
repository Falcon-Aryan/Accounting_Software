from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
import json
import random
from ..base.base_models import BaseDocument, LineItem
from ..products.models import Product
import traceback

INVOICE_STATUSES = [
    'draft',
    'sent',
    'paid',
    'overdue',
    'void'
]
PAYMENT_METHODS = ['cash', 'bank_transfer', 'credit_card', 'check', 'other']
PAYMENT_TERMS = ['due_on_receipt', 'net_15', 'net_30', 'net_60', 'custom']

@dataclass
class Payment:
    """Represents a payment for an invoice"""
    id: str
    date: str
    amount: float
    payment_method: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    transaction_id: Optional[str] = None  # Link to transaction

    def __post_init__(self):
        """Set created_at if not provided"""
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create a Payment instance from a dictionary"""
        return cls(
            id=data.get('id', ''),
            date=data.get('date', ''),
            amount=float(data.get('amount', 0.0)),
            payment_method=data.get('payment_method', ''),
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            transaction_id=data.get('transaction_id')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Payment instance to dictionary"""
        return {
            'id': self.id,
            'date': self.date,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_at': self.created_at,
            'transaction_id': self.transaction_id
        }

@dataclass
class Invoice(BaseDocument):
    """Represents an Invoice entry"""

    invoice_no: str = field(default_factory=lambda: f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000,9999)}")
    invoice_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    due_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    customer_name: str = ""
    balance_due: float = 0.0
    payments: List[Payment] = field(default_factory=list)
    sent_at: Optional[str] = None
    voided_at: Optional[str] = None
    void_reason: Optional[str] = None
    last_payment_date: Optional[str] = None
    converted_from_estimate: Optional[Dict] = None

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @staticmethod
    def get_user_data_file(uid: str) -> str:
        """Get the path to the user's invoices.json file"""
        return os.path.join(Invoice.BASE_DIR, 'data', uid, 'invoices.json')

    @staticmethod
    def generate_invoice_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(1000, 9999))
            second_half = str(random.randint(1000, 9999))
            id = f"{first_half}-{second_half}"
            return id

    def save(self, uid: str) -> None:
        """Save the invoice to the user's invoices.json file"""
        file_path = Invoice.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                data = {
                "invoices": [], 
                "summary": {
                    "draft_count": 0,
                    "sent_count": 0,
                    "paid_count": 0,
                    "overdue_count": 0,
                    "cancelled_count": 0,
                    "void_count": 0,
                    "draft_amount": 0.0,
                    "sent_amount": 0.0,
                    "paid_amount": 0.0,
                    "overdue_amount": 0.0,
                    "void_amount": 0.0,
                    "total_receivable": 0.0,
                    "total_collected": 0.0
                },
                "metadata": {
                    "lastUpdated": datetime.utcnow().isoformat(),
                    "createdAt": datetime.utcnow().isoformat()
                }
            }

            # Remove existing invoice if it exists
            data['invoices'] = [inv for inv in data['invoices'] if inv['id'] != self.id]
            
            # Add updated invoice
            data['invoices'].append(self.to_dict())
            data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error saving invoice: {str(e)}")

    @staticmethod
    def get_all(uid: str) -> List['Invoice']:
        """Get all invoices"""
        try:
            file_path = Invoice.get_user_data_file(uid)
            print(f"Looking for file at: {file_path}")

            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return []

            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Loaded data: {data}")
                invoices_data = data.get('invoices', [])
                print(f"Invoices data: {invoices_data}")
                
                invoices = []   
                for invoice_data in invoices_data:
                    try:
                        invoice = Invoice.from_dict(invoice_data)
                        invoices.append(invoice)
                    except Exception as e:
                        print(f"Error converting invoice {invoice_data.get('id')}: {str(e)}")
                        continue
            
            print(f"Converted invoices: {invoices}")
            return invoices
        except Exception as e:
            print(f"Error loading invoices: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
            return []

    @staticmethod
    def get_by_id(uid: str, id: str) -> Optional['Invoice']:
        """Get invoice by ID"""
        try:
            file_path = Invoice.get_user_data_file(uid)
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r') as f:
                data = json.load(f)
                invoice_data = next((inv for inv in data.get('invoices', []) if inv['id'] == id), None)
                return Invoice.from_dict(invoice_data) if invoice_data else None
        except Exception as e:
            print(f"Error loading invoice: {str(e)}")
            return None

    def delete(self, uid: str) -> None:
        """Delete the invoice from the user's invoices.json file"""
        file_path = Invoice.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Remove the invoice
                data['invoices'] = [inv for inv in data['invoices'] if inv['id'] != self.id]
                data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

                # Save the updated data
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error deleting invoice: {str(e)}")

    def __post_init__(self):
        """Calculate totals and set timestamps"""
        super().__post_init__()  # Call parent's post_init first
        
        # Convert payments from dict to Payment objects
        if isinstance(self.payments, list) and self.payments and isinstance(self.payments[0], dict):
            self.payments = [Payment(**payment) for payment in self.payments]

        # Calculate balance due using BaseDocument's total
        self.balance_due = self.total - sum(payment.amount for payment in self.payments)

        # Set last payment date
        if self.payments:
            self.last_payment_date = max(payment.date for payment in self.payments)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """Create an Invoice instance from a dictionary"""

        try:
            # Handle payments conversion
            payments = [Payment.from_dict(p) for p in data.get('payments', [])]
            
            # Handle line items conversion
            line_items = [LineItem.from_dict(item) if isinstance(item, dict) else item 
                        for item in data.get('line_items', [])]

            # Create a copy of the data to avoid modifying the original
            invoice_data = {
                'id': data['id'],
                'customer_id': data['customer_id'],
                'invoice_no': data.get('invoice_no', ''),
                'invoice_date': data.get('invoice_date', ''),
                'due_date': data.get('due_date', ''),
                'customer_name': data.get('customer_name', ''),
                'line_items': line_items,
                'payments': payments,
                'sent_at': data.get('sent_at'),
                'voided_at': data.get('voided_at'),
                'void_reason': data.get('void_reason'),
                'last_payment_date': data.get('last_payment_date'),
                'converted_from_estimate': data.get('converted_from_estimate'),
                'notes': data.get('notes', ''),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'status': data.get('status', 'draft'),
                'payment_terms': data.get('payment_terms', 'net_30'),
                'subtotal': data.get('subtotal', 0.0),
                'total': data.get('total', 0.0),
                'balance_due': data.get('balance_due', 0.0),
                'date': data.get('date', '')
            }

            return cls(**invoice_data)
        except Exception as e:
            print(f"Error in from_dict: {str(e)}")
            print(f"Data causing error: {data}")
            print(traceback.format_exc())
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert Invoice instance to dictionary"""
        base_dict = super().to_dict()
        invoice_dict = {
            'invoice_no': self.invoice_no,
            'invoice_date': self.invoice_date,
            'due_date': self.due_date,
            'customer_name': self.customer_name,
            'balance_due': self.balance_due,
            'payments': [p.to_dict() for p in self.payments],
            'sent_at': self.sent_at,
            'voided_at': self.voided_at,
            'void_reason': self.void_reason,
            'last_payment_date': self.last_payment_date,
            'converted_from_estimate': self.converted_from_estimate
        }
        return {**base_dict, **invoice_dict}

@dataclass
class InvoicesSummary:
    """Summary information about invoices"""
    draft_count: int = 0
    sent_count: int = 0
    paid_count: int = 0
    overdue_count: int = 0
    cancelled_count: int = 0
    void_count: int = 0
    draft_amount: float = 0.0
    sent_amount: float = 0.0
    paid_amount: float = 0.0
    overdue_amount: float = 0.0
    void_amount: float = 0.0
    total_receivable: float = 0.0
    total_collected: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert InvoicesSummary instance to dictionary"""
        return {
            'draft_count': self.draft_count,
            'sent_count': self.sent_count,
            'paid_count': self.paid_count,
            'overdue_count': self.overdue_count,
            'cancelled_count': self.cancelled_count,
            'void_count': self.void_count,
            'draft_amount': self.draft_amount,
            'sent_amount': self.sent_amount,
            'paid_amount': self.paid_amount,
            'overdue_amount': self.overdue_amount,
            'void_amount': self.void_amount,
            'total_receivable': self.total_receivable,
            'total_collected': self.total_collected
        }
