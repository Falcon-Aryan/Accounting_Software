from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
import json
import random
from ..products.models import Product

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
class InvoiceLineItem:
    """Represents a line item in an invoice"""
    product_id: str
    quantity: float = 1.0
    unit_price: float = 0.0
    description: str = ""
    total: float = 0.0

    def __post_init__(self):
        """Calculate total after initialization"""
        self.total = self.unit_price * self.quantity

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InvoiceLineItem':
        """Create an InvoiceLineItem instance from a dictionary"""
        return cls(
            product_id=data.get('product_id', ''),
            quantity=float(data.get('quantity', 1.0)),
            unit_price=float(data.get('unit_price', 0.0)),
            description=data.get('description', ''),
            total=float(data.get('total', 0.0))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert InvoiceLineItem instance to dictionary"""
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'description': self.description,
            'total': self.total
        }

@dataclass
class Invoice:
    """Represents an Invoice entry"""
    id: str
    invoice_no: str
    invoice_date: str
    due_date: str
    customer_name: str
    status: str
    line_items: List[InvoiceLineItem] = field(default_factory=list)
    total_amount: float = 0.0
    balance_due: float = 0.0
    payments: List[Payment] = field(default_factory=list)
    payment_terms: str = 'due_on_receipt'
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
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
                data = {"invoices": [], "metadata": {"lastUpdated": datetime.utcnow().isoformat()}}

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
            if not os.path.exists(file_path):
                return []
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [Invoice.from_dict(invoice_data) for invoice_data in data.get('invoices', [])]
        except Exception as e:
            print(f"Error loading invoices: {str(e)}")
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
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

        # Convert line_items from dict to InvoiceLineItem objects
        if isinstance(self.line_items, list) and self.line_items and isinstance(self.line_items[0], dict):
            self.line_items = [InvoiceLineItem(**item) for item in self.line_items]

        # Calculate total amount
        self.total_amount = sum(item.total for item in self.line_items)
        self.balance_due = self.total_amount - sum(payment.amount for payment in self.payments)

        # Convert payments from dict to Payment objects
        if isinstance(self.payments, list) and self.payments and isinstance(self.payments[0], dict):
            self.payments = [Payment(**payment) for payment in self.payments]

        # Set last payment date
        if self.payments:
            self.last_payment_date = max(payment.date for payment in self.payments)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """Create an Invoice instance from a dictionary"""
        line_items = [InvoiceLineItem.from_dict(item) for item in data.get('line_items', [])]
        payments = [Payment.from_dict(p) for p in data.get('payments', [])]
        
        return cls(
            id=data.get('id', ''),
            invoice_no=data.get('invoice_no', ''),
            invoice_date=data.get('invoice_date', ''),
            due_date=data.get('due_date', ''),
            customer_name=data.get('customer_name', ''),
            status=data.get('status', 'draft'),
            line_items=line_items,
            payment_terms=data.get('payment_terms', 'due_on_receipt'),
            payments=payments,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            sent_at=data.get('sent_at'),
            voided_at=data.get('voided_at'),
            void_reason=data.get('void_reason'),
            last_payment_date=data.get('last_payment_date'),
            converted_from_estimate=data.get('converted_from_estimate')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Invoice instance to dictionary"""
        return {
            'id': self.id,
            'invoice_no': self.invoice_no,
            'invoice_date': self.invoice_date,
            'due_date': self.due_date,
            'customer_name': self.customer_name,
            'status': self.status,
            'line_items': [item.to_dict() for item in self.line_items],
            'total_amount': self.total_amount,
            'balance_due': self.balance_due,
            'payments': [p.to_dict() for p in self.payments],
            'payment_terms': self.payment_terms,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'sent_at': self.sent_at,
            'voided_at': self.voided_at,
            'void_reason': self.void_reason,
            'last_payment_date': self.last_payment_date,
            'converted_from_estimate': self.converted_from_estimate
        }

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
