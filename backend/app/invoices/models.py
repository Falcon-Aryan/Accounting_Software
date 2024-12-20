from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

INVOICE_STATUSES = [
    'draft',
    'posted',
    'paid',
    'overdue',
    'void'
]
PAYMENT_METHODS = ['cash', 'bank_transfer', 'credit_card', 'check', 'other']
PAYMENT_TERMS = ['due_on_receipt', 'net_15', 'net_30', 'net_60', 'custom']

@dataclass
class Product:
    """Represents a product or service in an invoice"""
    name: str
    description: str
    price: float
    quantity: float = 1.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0

    def __post_init__(self):
        """Calculate tax and total after initialization"""
        self.tax_amount = self.price * self.quantity * (self.tax_rate / 100)
        self.total = (self.price * self.quantity) + self.tax_amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create a Product instance from a dictionary"""
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            price=float(data.get('price', 0.0)),
            quantity=float(data.get('quantity', 1.0)),
            tax_rate=float(data.get('tax_rate', 0.0))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Product instance to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'quantity': self.quantity,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'total': self.total
        }

@dataclass
class Payment:
    """Represents a payment for an invoice"""
    id: str
    date: str
    amount: float
    payment_method: str
    reference: Optional[str] = None
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
            reference=data.get('reference'),
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
            'reference': self.reference,
            'notes': self.notes,
            'created_at': self.created_at,
            'transaction_id': self.transaction_id
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
    products: List[Product]
    total_amount: float = 0.0
    balance_due: float = 0.0
    payments: List[Payment] = field(default_factory=list)
    payment_terms: str = 'due_on_receipt'
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_payment_date: Optional[str] = None
    converted_from_estimate: Optional[Dict] = None

    def __post_init__(self):
        """Calculate totals and set timestamps"""
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
            
        # Calculate total amount
        self.total_amount = sum(product.total for product in self.products)
        
        # Calculate balance due
        total_paid = sum(payment.amount for payment in self.payments)
        self.balance_due = self.total_amount - total_paid
        
        # Set last payment date
        if self.payments:
            self.last_payment_date = max(payment.date for payment in self.payments)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """Create an Invoice instance from a dictionary"""
        products = [Product.from_dict(p) for p in data.get('products', [])]
        payments = [Payment.from_dict(p) for p in data.get('payments', [])]
        
        return cls(
            id=data.get('id', ''),
            invoice_no=data.get('invoice_no', ''),
            invoice_date=data.get('invoice_date', ''),
            due_date=data.get('due_date', ''),
            customer_name=data.get('customer_name', ''),
            status=data.get('status', 'draft'),
            products=products,
            payment_terms=data.get('payment_terms', 'due_on_receipt'),
            payments=payments,
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
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
            'products': [p.to_dict() for p in self.products],
            'total_amount': self.total_amount,
            'balance_due': self.balance_due,
            'payments': [p.to_dict() for p in self.payments],
            'payment_terms': self.payment_terms,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_payment_date': self.last_payment_date,
            'converted_from_estimate': self.converted_from_estimate
        }

@dataclass
class InvoicesSummary:
    """Summary information about invoices"""
    # Counts by status
    draft_count: int = 0
    posted_count: int = 0
    paid_count: int = 0
    overdue_count: int = 0
    cancelled_count: int = 0
    void_count: int = 0
    
    # Amounts by status
    draft_amount: float = 0.0
    posted_amount: float = 0.0
    paid_amount: float = 0.0
    overdue_amount: float = 0.0
    void_amount: float = 0.0
    
    # Payment tracking
    total_receivable: float = 0.0  # Total amount still to be collected (excludes paid and cancelled)
    total_collected: float = 0.0   # Total amount collected so far
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert InvoicesSummary instance to dictionary"""
        return {
            # Counts
            'draft_count': self.draft_count,
            'posted_count': self.posted_count,
            'paid_count': self.paid_count,
            'overdue_count': self.overdue_count,
            'cancelled_count': self.cancelled_count,
            'void_count': self.void_count,
            
            # Amounts
            'draft_amount': self.draft_amount,
            'posted_amount': self.posted_amount,
            'paid_amount': self.paid_amount,
            'overdue_amount': self.overdue_amount,
            'void_amount': self.void_amount,
            
            # Payment tracking
            'total_receivable': self.total_receivable,
            'total_collected': self.total_collected
        }
