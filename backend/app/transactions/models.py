from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum, auto
import os
import json

class TransactionType(Enum):
    """Types of transactions"""
    SALE = 'sale'                    # Sale of goods or services
    PURCHASE = 'purchase'            # Purchase of goods or services
    PAYMENT_RECEIVED = 'payment_received'  # Money received from customers
    PAYMENT_MADE = 'payment_made'    # Money paid to vendors
    EXPENSE = 'expense'              # Business expenses
    EQUITY = 'equity'                # Owner investments or withdrawals
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
    
    # Equity sub-types
    OWNER_INVESTMENT = 'owner_investment'
    OWNER_WITHDRAWAL = 'owner_withdrawal'
    RETAINED_EARNINGS = 'retained_earnings'
    
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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Static methods for file handling
    @staticmethod
    def get_user_data_file(uid: str) -> str:
        """Get the path to the user's transactions.json file"""
        user_dir = os.path.join(Transaction.BASE_DIR, 'data', uid)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return os.path.join(user_dir, 'transactions.json')

    @staticmethod
    def load_user_transactions(uid: str) -> Dict:
        """Load transactions data from JSON file"""
        file_path = Transaction.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return {'transactions': []}
        except Exception as e:
            print(f"Error loading transactions: {str(e)}")
            return {'transactions': []}

    @staticmethod
    def save_user_transactions(uid: str, data: Dict) -> bool:
        """Save transactions data to JSON file"""
        file_path = Transaction.get_user_data_file(uid)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving transactions: {str(e)}")
            return False

    # Instance fields
    id: str
    date: str
    entries: List[TransactionEntry]
    status: str  # 'draft', 'posted', or 'void'
    description: str
    transaction_type: str
    sub_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    customer_name: Optional[str] = None
    amount: Optional[float] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    posted_at: Optional[str] = None
    posted_by: Optional[str] = None
    voided_at: Optional[str] = None
    voided_by: Optional[str] = None
    metadata: Optional[Dict] = None
    products: Optional[List[Dict]] = None
    invoice_total: Optional[float] = None
    invoice_paid: Optional[float] = None
    invoice_balance: Optional[float] = None
    invoice_status: Optional[str] = None
    last_payment_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction instance from a dictionary"""
        # Convert entries to TransactionEntry objects
        entries = [TransactionEntry.from_dict(entry) for entry in data.get('entries', [])]
        
        # Create the Transaction object
        return cls(
            id=data.get('id', ''),
            date=data.get('date', ''),
            description=data.get('description', ''),
            transaction_type=data.get('transaction_type', ''),
            sub_type=data.get('sub_type', ''),
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            customer_name=data.get('customer_name'),
            amount=float(data.get('amount', 0)) if data.get('amount') is not None else None,
            status=data.get('status', 'draft'),
            entries=entries,
            created_at=data.get('created_at'),
            created_by=data.get('created_by'),
            updated_at=data.get('updated_at'),
            updated_by=data.get('updated_by'),
            posted_at=data.get('posted_at'),
            posted_by=data.get('posted_by'),
            voided_at=data.get('voided_at'),
            voided_by=data.get('voided_by'),
            metadata=data.get('metadata'),
            products=data.get('products'),
            invoice_total=float(data.get('invoice_total', 0)) if data.get('invoice_total') is not None else None,
            invoice_paid=float(data.get('invoice_paid', 0)) if data.get('invoice_paid') is not None else None,
            invoice_balance=float(data.get('invoice_balance', 0)) if data.get('invoice_balance') is not None else None,
            invoice_status=data.get('invoice_status'),
            last_payment_date=data.get('last_payment_date')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Transaction instance to dictionary"""
        return {
            'id': self.id,
            'date': self.date,
            'description': self.description,
            'transaction_type': self.transaction_type,
            'sub_type': self.sub_type,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'customer_name': self.customer_name,
            'amount': self.amount,
            'status': self.status,
            'entries': [entry.to_dict() for entry in self.entries],
            'created_at': self.created_at,
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_by': self.updated_by,
            'posted_at': self.posted_at,
            'posted_by': self.posted_by,
            'voided_at': self.voided_at,
            'voided_by': self.voided_by,
            'metadata': self.metadata,
            'products': self.products,
            'invoice_total': self.invoice_total,
            'invoice_paid': self.invoice_paid,
            'invoice_balance': self.invoice_balance,
            'invoice_status': self.invoice_status,
            'last_payment_date': self.last_payment_date
        }

    def __post_init__(self):
        """Set timestamps if not provided"""
        now = datetime.utcnow().date().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
            
        # Convert entries to TransactionEntry objects if they're dictionaries
        if self.entries and isinstance(self.entries[0], dict):
            self.entries = [TransactionEntry.from_dict(entry) for entry in self.entries]

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the transaction"""
        try:
            # Basic validation
            if not self.id:
                return False, "Transaction ID is required"
            if not self.date:
                return False, "Transaction date is required"
            if not self.entries:
                return False, "Transaction must have at least one entry"
                
            # Validate entries
            total_debits = 0
            total_credits = 0
            account_entries = {}  # Track account entries by type
            
            for entry in self.entries:
                # Validate entry fields
                if not entry.accountId:
                    return False, "Account ID is required for all entries"
                if not entry.accountName:
                    return False, "Account name is required for all entries"
                if entry.amount <= 0:
                    return False, "Amount must be positive for all entries"
                if entry.type not in ['debit', 'credit']:
                    return False, "Entry type must be either 'debit' or 'credit'"
                    
                # Track totals
                if entry.type == 'debit':
                    total_debits += entry.amount
                else:
                    total_credits += entry.amount
                    
                # Check for duplicate account entries of the same type
                entry_key = f"{entry.accountId}_{entry.type}"
                if entry_key in account_entries:
                    return False, f"Duplicate {entry.type} entry for account {entry.accountId}"
                account_entries[entry_key] = entry
                
            # Validate debits equal credits
            if abs(total_debits - total_credits) > 0.01:  # Allow for small floating point differences
                return False, "Total debits must equal total credits"
                
            return True, None
            
        except Exception as e:
            return False, str(e)
