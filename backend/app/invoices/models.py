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

INVOICE_STATUSES = [
    'draft',
    'sent', 
    'accepted',
    'declined',
    'paid',
    'partially_paid',
    'overdue',
    'voided'
]

PAYMENT_TERMS = [
    'net15',
    'net30',
    'net60',
    'due_on_receipt'
]

VALID_STATUS_TRANSITIONS = {
    'draft': ['sent', 'voided'],
    'sent': ['accepted', 'declined', 'voided'],
    'accepted': ['paid', 'voided'],
    'declined': ['voided'],
    'paid': ['voided'],
    'partially_paid': ['paid', 'voided'],
    'overdue': ['paid', 'voided'],
    'voided': []
}

@dataclass
class InvoiceLineItem:
    """Line item for invoices"""
    type: str  # 'product' or 'service'
    item_id: str
    name: str
    price: float
    quantity: float = 1.0
    description: Optional[str] = None
    amount: float = 0.0

    def __post_init__(self):
        self.amount = round(self.quantity * self.price, 2)

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
    def from_dict(cls, data: Dict[str, Any]) -> 'InvoiceLineItem':
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
            return cls(
                type='product',
                item_id=item_id,
                name=product.name,
                price=product.price,
                quantity=quantity,
                description=description
            )
        elif item_id.startswith('SERV'):
            # Fetch service details
            service = Service.get_service(item_id)
            if not service:
                raise ValueError(f"Service not found: {item_id}")
            return cls(
                type='service',
                item_id=item_id,
                name=service.name,
                price=service.price,
                quantity=quantity,
                description=description
            )
        else:
            raise ValueError(f"Invalid item_id format: {item_id}")

@dataclass
class InvoicePayment:
    """Represents a payment for an invoice"""
    reference_id: str = ""
    transaction_id: str = ""
    amount: float = 0.0
    payment_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payment_method: str = ""  # cash, check, credit_card, bank_transfer
    notes: Optional[str] = None
    check_number: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        if not self.reference_id:
            self.reference_id = self.generate_reference_id()
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

    @staticmethod
    def generate_reference_id() -> str:
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"REFN{first_half}-{second_half}"
            return id

    @staticmethod
    def generate_transaction_id() -> str:
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"TRXN{first_half}-{second_half}"
            return id

    def to_dict(self) -> Dict:
        return {
            'reference_id': self.reference_id,
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'check_number': self.check_number,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InvoicePayment':
        return cls(**data)



@dataclass
class Invoice: 
    """Represents an Invoice in Appwrite"""
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "invoices"

    user_id: str
    invoice_id: str = ""
    invoice_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    due_date: str = field(default_factory=lambda: (datetime.utcnow() + timedelta(days=30)).isoformat())
    customer_id: str = ""
    status: str = "draft"
    payment_terms: str = "net30"
    total: float = 0.0
    amount_paid: float = 0.0
    balance: float = 0.0
    line_items: List[InvoiceLineItem] = field(default_factory=list)
    payments: List[InvoicePayment] = field(default_factory=list)
    notes: Optional[str] = None
    document_id: Optional[str] = None
    sent_at: Optional[str] = None
    accepted_at: Optional[str] = None
    declined_at: Optional[str] = None
    decline_reason: Optional[str] = None
    paid_at: Optional[str] = None
    voided_at: Optional[str] = None
    void_reason: Optional[str] = None
    converted_from: Optional[str] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        if self.status not in INVOICE_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(INVOICE_STATUSES)}")
        if self.payment_terms not in PAYMENT_TERMS:
            raise ValueError(f"Invalid payment terms. Must be one of: {', '.join(PAYMENT_TERMS)}")
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        # Calculate due date based on payment terms
        if not self.due_date:
            days = int(self.payment_terms.replace('net', ''))
            self.due_date = (datetime.fromisoformat(self.invoice_date) + timedelta(days=days)).isoformat()
        self._calculate_total()
        self._calculate_amount_paid()
        self._calculate_balance()

    def _calculate_total(self):
        """Calculate total from line items"""
        self.total = round(sum(item.amount for item in self.line_items), 2)
        self._calculate_balance()

    def _calculate_amount_paid(self):
        """Calculate total amount paid from payments"""
        self.amount_paid = round(sum(payment.amount for payment in self.payments), 2)
        self._calculate_balance()

    def _calculate_balance(self):
        """Calculate balance from total and amount_paid"""
        self.balance = round(self.total - self.amount_paid, 2)

        if abs(self.balance) <= 0.01 and self.amount_paid > 0:  # Handle tiny rounding differences
            self.balance = 0.0
            self.status = "paid"
            if not self.paid_at:
                self.paid_at = datetime.utcnow().isoformat()
        elif self.balance > 0 and self.amount_paid > 0:
            self.status = "partially_paid"
        elif self.balance > 0 and datetime.fromisoformat(self.due_date) < datetime.utcnow():
            if self.status not in ['voided', 'paid']:
                self.status = "overdue"

    def update_status(self, new_status: str) -> None:
        """Update invoice status with validation"""
        if new_status not in INVOICE_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(INVOICE_STATUSES)}")
            
        # Check if the status transition is valid
        if self.status not in VALID_STATUS_TRANSITIONS or new_status not in VALID_STATUS_TRANSITIONS[self.status]:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
            
        # Set appropriate timestamps
        current_time = datetime.utcnow().isoformat()
        
        if new_status == 'sent' and not self.sent_at:
            self.sent_at = current_time
        elif new_status == 'paid' and not self.paid_at:
            self.paid_at = current_time
        elif new_status == 'voided' and not self.voided_at:
            self.voided_at = current_time
            
        self.status = new_status
        self.updated_at = current_time

    def add_payment(self, payment: InvoicePayment) -> None:
        """Add a payment to the invoice with validation"""
        if self.status == 'voided':
            raise ValueError("Cannot add payment to a voided invoice")
        if payment.amount <= 0:
            raise ValueError("Payment amount must be greater than 0")
        if payment.amount > self.balance:
            raise ValueError("Payment amount cannot exceed invoice balance")
            
        self.payments.append(payment)
        self._calculate_amount_paid()
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self, for_appwrite: bool = False) -> Dict:
        """Convert invoice to dictionary"""
        data = {
            'user_id': self.user_id,
            'invoice_id': self.invoice_id,
            'invoice_date': self.invoice_date,
            'due_date': self.due_date,
            'customer_id': self.customer_id,
            'status': self.status,
            'payment_terms': self.payment_terms,
            'total': self.total,
            'amount_paid': self.amount_paid,
            'balance': self.balance,
            'notes': self.notes,
            'sent_at': self.sent_at,
            'accepted_at': self.accepted_at,
            'declined_at': self.declined_at,
            'decline_reason': self.decline_reason,
            'paid_at': self.paid_at,
            'voided_at': self.voided_at,
            'void_reason': self.void_reason,
            'converted_from': self.converted_from,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        # Handle line items and payments serialization
        if for_appwrite:
            data['line_items'] = json.dumps([item.to_dict() for item in self.line_items])
            data['payments'] = json.dumps([payment.to_dict() for payment in self.payments])
        else:
            data['line_items'] = [item.to_dict() for item in self.line_items]
            data['payments'] = [payment.to_dict() for payment in self.payments]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any], document_id: Optional[str] = None):
        """Create invoice from dictionary"""
        # Handle line items deserialization
        line_items_data = data.get('line_items', '[]')
        if isinstance(line_items_data, str):
            line_items_data = json.loads(line_items_data)
        line_items = [InvoiceLineItem.from_dict(item) for item in line_items_data]
        
        # Handle payments deserialization
        payments_data = data.get('payments', '[]')
        if isinstance(payments_data, str):
            payments_data = json.loads(payments_data)
        payments = [InvoicePayment.from_dict(payment) for payment in payments_data]
        
        # Create invoice instance
        invoice = cls(
            user_id=data['user_id'],
            invoice_id=data.get('invoice_id', ''),
            invoice_date=data.get('invoice_date', datetime.utcnow().isoformat()),
            due_date=data.get('due_date'),
            customer_id=data.get('customer_id', ''),
            status=data.get('status', 'draft'),
            payment_terms=data.get('payment_terms', 'net30'),
            total=float(data.get('total', 0)),
            amount_paid=float(data.get('amount_paid', 0)),
            balance=float(data.get('balance', 0)),
            line_items=line_items,
            payments=payments,
            notes=data.get('notes'),
            sent_at=data.get('sent_at'),
            accepted_at=data.get('accepted_at'),
            declined_at=data.get('declined_at'),
            decline_reason=data.get('decline_reason'),
            paid_at=data.get('paid_at'),
            voided_at=data.get('voided_at'),
            void_reason=data.get('void_reason'),
            converted_from=data.get('converted_from'),
            created_at=data.get('created_at', datetime.utcnow().isoformat()),
            updated_at=data.get('updated_at', datetime.utcnow().isoformat()),
            document_id=document_id
        )
        
        return invoice

    @staticmethod
    def generate_invoice_id() -> str:
        """Generate a random invoice ID with a specific format"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"INV{first_half}-{second_half}"
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
    def create_invoice(cls, user_id: str, customer_id: str, line_items: List['InvoiceLineItem'], payment_terms: str = 'net30', converted_from: Optional[str] = None, notes: Optional[str] = None):
        """Create a new invoice"""
        # Validate customer
        if not cls.validate_customer(user_id, customer_id):
            raise ValueError(f"Customer {customer_id} not found or does not belong to user {user_id}")
            
        # Generate a unique invoice ID
        invoice_id = cls.generate_invoice_id()
        
        # Create the invoice instance
        invoice = cls(
            user_id=user_id,
            invoice_id=invoice_id,
            customer_id=customer_id,
            line_items=line_items,
            payment_terms=payment_terms,
            converted_from=converted_from,
            notes=notes
        )
        
        # Return the invoice object
        return invoice

    @classmethod
    def get_database(cls):
        """Get Appwrite database instance"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)

    @classmethod
    def get_invoice_by_id(cls, invoice_id: str, user_id: str = None):
        """Get an invoice by invoice ID. If user_id is provided, verify ownership."""
        try:
            db = cls.get_database()
            # Query by invoice_id instead of document_id
            result = db.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('invoice_id', invoice_id)]
            )
            
            if not result['documents']:
                raise Exception("Invoice not found")   
                
            invoice_doc = result['documents'][0]
            
            if user_id and invoice_doc['user_id'] != user_id:
                raise Exception("Unauthorized access to invoice")
                
            return cls.from_dict(invoice_doc, invoice_doc['$id'])
            
        except Exception as e:
            raise Exception(f"Error getting invoice: {str(e)}")

    @classmethod
    def get_invoices_by_user(cls, user_id: str):
        """Get all invoices for a specific user"""
        try:
            db = cls.get_database()
            invoices = db.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            return [cls.from_dict(doc, doc['$id']) for doc in invoices['documents']]
            
        except Exception as e:
            raise Exception(f"Error getting invoices: {str(e)}")

    @classmethod
    def update_invoice(cls, invoice_id: str, user_id: str, data: Dict):
        """Update an invoice, verifying ownership first"""
        try:
            # Get existing invoice
            existing = cls.get_invoice_by_id(invoice_id, user_id)
            
            # Update the invoice with new data
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            
            # If updating status, validate it
            if 'status' in data and data['status'] not in INVOICE_STATUSES:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(INVOICE_STATUSES)}")
            
            # Update in database
            db = cls.get_database()
            invoice_doc = db.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=existing.document_id,  # Use the stored document_id for update
                data=existing.to_dict(for_appwrite=True)
            )
            
            return cls.from_dict(invoice_doc, invoice_doc['$id'])
            
        except Exception as e:
            raise Exception(f"Error updating invoice: {str(e)}")

    @classmethod
    def delete_invoice(cls, invoice_id: str, user_id: str):
        """Delete an invoice, verifying ownership first"""
        try:
            # Verify ownership and get document_id
            existing = cls.get_invoice_by_id(invoice_id, user_id)
            
            # Delete from database using document_id
            db = cls.get_database()
            db.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=existing.document_id
            )
            
        except Exception as e:
            raise Exception(f"Error deleting invoice: {str(e)}")