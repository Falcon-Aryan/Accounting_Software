from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum, auto

class TransactionType(Enum):
    """Types of transactions"""
    PAYMENT = 'payment'
    INVOICE = 'invoice'
    BILL = 'bill'
    EXPENSE = 'expense'
    JOURNAL = 'journal'
    TRANSFER = 'transfer'
    OTHER = 'other'

@dataclass
class TransactionEntry:
    """Represents a single entry in a transaction (debit or credit)"""
    accountId: str
    amount: float
    type: str  # 'debit' or 'credit'
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionEntry':
        """Create a TransactionEntry instance from a dictionary"""
        return cls(
            accountId=data.get('accountId', ''),
            amount=float(data.get('amount', 0.0)),
            type=data.get('type', ''),
            description=data.get('description')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert TransactionEntry instance to dictionary"""
        return {
            'accountId': self.accountId,
            'amount': self.amount,
            'type': self.type,
            'description': self.description
        }

@dataclass
class Transaction:
    """Represents a complete transaction with multiple entries"""
    id: str
    date: str  # Changed from date to str to match other date fields
    entries: List[TransactionEntry]
    status: str  # 'draft', 'posted', or 'void'
    description: Optional[str] = None
    transaction_type: TransactionType = TransactionType.OTHER  # Added transaction type
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
        # Convert entries
        entries = [TransactionEntry.from_dict(e) for e in data.get('entries', [])]
        
        # Convert transaction type
        transaction_type = data.get('transaction_type')
        if isinstance(transaction_type, str):
            transaction_type = TransactionType(transaction_type)
        elif not isinstance(transaction_type, TransactionType):
            transaction_type = TransactionType.OTHER
            
        return cls(
            id=data.get('id', ''),
            date=data.get('date', ''),
            entries=entries,
            status=data.get('status', 'draft'),
            description=data.get('description'),
            transaction_type=transaction_type,
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            customer_name=data.get('customer_name'),  # Added customer name
            products=data.get('products', []),  # Added products list
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
            'entries': [e.to_dict() for e in self.entries],
            'status': self.status,
            'description': self.description,
            'transaction_type': self.transaction_type.value,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'customer_name': self.customer_name,  # Added customer name
            'products': self.products,  # Added products list
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
