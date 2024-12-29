from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum, auto

class TransactionType(Enum):
    """Types of transactions"""
    SALE = 'sale'                    # Sale of goods or services
    PURCHASE = 'purchase'            # Purchase of goods or services
    PAYMENT_RECEIVED = 'payment_received'  # Money received from customers
    PAYMENT_MADE = 'payment_made'    # Money paid to vendors
    EXPENSE = 'expense'              # Business expenses
    JOURNAL = 'journal'              # Manual journal entries
    TRANSFER = 'transfer'            # Fund transfers between accounts
    ADJUSTMENT = 'adjustment'        # Inventory or account adjustments
    ESTIMATE = 'estimate'            # Customer estimates/quotes
    INVOICE = 'invoice'              # Customer invoices
    OTHER = 'other'                  # Other transactions

class TransactionSubType(Enum):
    """Sub-types for further transaction categorization"""
    # Sale sub-types
    PRODUCT_SALE = 'product_sale'
    SERVICE_SALE = 'service_sale'
    
    # Purchase sub-types
    INVENTORY_PURCHASE = 'inventory_purchase'
    SUPPLY_PURCHASE = 'supply_purchase'
    
    # Payment sub-types
    CASH_PAYMENT = 'cash_payment'
    BANK_TRANSFER = 'bank_transfer'
    CREDIT_CARD = 'credit_card'
    CHECK = 'check'
    
    # Expense sub-types
    UTILITIES = 'utilities'
    RENT = 'rent'
    PAYROLL = 'payroll'
    ADVERTISING = 'advertising'
    OFFICE_SUPPLIES = 'office_supplies'
    
    # Adjustment sub-types
    INVENTORY_ADJUSTMENT = 'inventory_adjustment'
    ACCOUNT_ADJUSTMENT = 'account_adjustment'
    
    # Estimate sub-types
    ESTIMATE_DRAFT = 'estimate_draft'
    ESTIMATE_SENT = 'estimate_sent'
    ESTIMATE_ACCEPTED = 'estimate_accepted'
    ESTIMATE_DECLINED = 'estimate_declined'
    ESTIMATE_EXPIRED = 'estimate_expired'
    ESTIMATE_CONVERTED = 'estimate_converted'
    
    # Invoice sub-types
    INVOICE_DRAFT = 'invoice_draft'
    INVOICE_POSTED = 'invoice_posted'
    INVOICE_PAID = 'invoice_paid'
    INVOICE_PARTIALLY_PAID = 'invoice_partially_paid'
    INVOICE_OVERDUE = 'invoice_overdue'
    INVOICE_VOID = 'invoice_void'
    
    OTHER = 'other'

@dataclass
class TransactionEntry:
    """Represents a single entry in a transaction (debit or credit)"""
    accountId: str
    accountName: str
    amount: float
    type: str  # 'debit' or 'credit'
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionEntry':
        """Create a TransactionEntry instance from a dictionary"""
        return cls(
            accountId=data.get('accountId', ''),
            accountName=data.get('accountName', ''),
            amount=float(data.get('amount', 0.0)),
            type=data.get('type', ''),
            description=data.get('description')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert TransactionEntry instance to dictionary"""
        return {
            'accountId': self.accountId,
            'accountName': self.accountName,
            'amount': self.amount,
            'type': self.type,
            'description': self.description
        }

@dataclass
class Transaction:
    """Represents a complete transaction with multiple entries"""
    id: str
    date: str
    entries: List[TransactionEntry]
    status: str  # 'draft', 'posted', or 'void'
    description: Optional[str] = None
    transaction_type: TransactionType = TransactionType.OTHER
    sub_type: TransactionSubType = TransactionSubType.OTHER
    metadata: Dict[str, Any] = None  # Additional context for the transaction
    reference_type: Optional[str] = None  # e.g., 'invoice_payment', 'bill_payment'
    reference_id: Optional[str] = None  # ID of the referenced document
    customer_name: Optional[str] = None  # Added customer name
    products: Optional[List[Dict[str, Any]]] = None  # Added products list
    created_at: Optional[str] = None  # Changed from datetime to str
    updated_at: Optional[str] = None
    posted_at: Optional[str] = None
    voided_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    posted_by: Optional[str] = None
    voided_by: Optional[str] = None

    def __post_init__(self):
        """Set timestamps if not provided"""
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction instance from a dictionary"""
        # Convert entries to TransactionEntry objects
        entries = [TransactionEntry.from_dict(entry) for entry in data.get('entries', [])]
        
        # Convert transaction_type string to enum
        transaction_type = data.get('transaction_type', 'other')
        try:
            transaction_type = TransactionType(transaction_type)
        except ValueError:
            transaction_type = TransactionType.OTHER

        # Convert sub_type string to enum
        sub_type = data.get('sub_type', 'other')
        try:
            sub_type = TransactionSubType(sub_type)
        except ValueError:
            sub_type = TransactionSubType.OTHER

        # Create the transaction
        return cls(
            id=data.get('id', ''),
            date=data.get('date', ''),
            entries=entries,
            status=data.get('status', 'draft'),
            description=data.get('description'),
            transaction_type=transaction_type,
            sub_type=sub_type,
            metadata=data.get('metadata', {}),
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            customer_name=data.get('customer_name'),
            products=data.get('products'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            posted_at=data.get('posted_at'),
            voided_at=data.get('voided_at'),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by'),
            posted_by=data.get('posted_by'),
            voided_by=data.get('voided_by')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Transaction instance to dictionary"""
        return {
            'id': self.id,
            'date': self.date,
            'entries': [entry.to_dict() for entry in self.entries],
            'status': self.status,
            'description': self.description,
            'transaction_type': self.transaction_type.value,
            'sub_type': self.sub_type.value,
            'metadata': self.metadata,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'customer_name': self.customer_name,
            'products': self.products,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'posted_at': self.posted_at,
            'voided_at': self.voided_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'posted_by': self.posted_by,
            'voided_by': self.voided_by
        }

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the transaction"""
        if not self.entries or len(self.entries) < 2:
            return False, "Transaction must have at least 2 entries"

        # Calculate total debits and credits
        total_debits = sum(entry.amount for entry in self.entries if entry.type == 'debit')
        total_credits = sum(entry.amount for entry in self.entries if entry.type == 'credit')

        # Check if transaction is balanced
        if abs(total_debits - total_credits) > 0.01:  # Using 0.01 to handle floating point precision
            return False, "Transaction is not balanced. Debits must equal credits."

        return True, None
