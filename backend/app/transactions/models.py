from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import sys
import random
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from app.chart_of_accounts.models import Account

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.data_models.transaction_types import TRANSACTION_TYPES, TRANSACTION_ACCOUNT_MAPPING, TRANSACTION_DETAIL_TYPE_MAPPING, TRANSACTION_STATUSES, VALID_STATUS_TRANSITIONS


@dataclass
class TransactionEntry:
    """Entry line for double-entry accounting transactions"""
    account_id: str
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    description: Optional[str] = None

    def __post_init__(self):
        """Validate the entry after initialization"""
        if self.debit_amount < 0 or self.credit_amount < 0:
            raise ValueError("Debit and credit amounts must be non-negative")
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError(
                "An entry cannot have both debit and credit amounts")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError(
                "Either debit or credit amount must be greater than zero")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'account_id': self.account_id,
            'debit_amount': self.debit_amount,
            'credit_amount': self.credit_amount,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionEntry':
        """Create TransactionEntry from dictionary"""
        return cls(
            account_id=data['account_id'],
            debit_amount=float(data.get('debit_amount', 0)),
            credit_amount=float(data.get('credit_amount', 0)),
            description=data.get('description')
        )


@dataclass
class Transaction:
    """Transaction model for double-entry accounting"""
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "transactions"

    user_id: str
    transaction_id: str = ""
    transaction_date: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())
    description: str = None
    type: str = 'journal_entry'
    status: str = 'draft'
    total_amount: float = 0
    notes: Optional[str] = None
    entries: List[TransactionEntry] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())
    modified_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())
    posted_at: Optional[str] = None
    voided_at: Optional[str] = None
    void_reason: Optional[str] = None

    def __post_init__(self):
        """Initialize transaction and validate entries"""
        if self.status not in TRANSACTION_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")
        if self.type not in TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type: {self.type}")
        self._validate_entries()
        self._calculate_total()

    @staticmethod
    def generate_transaction_id() -> str:
        """Generate a random 12-digit ID with TXN prefix"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            return f"TXN{first_half}-{second_half}"

    def update_status(self, new_status: str, void_reason: Optional[str] = None):
        """Update transaction status with validation"""
        if new_status not in TRANSACTION_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        if new_status not in VALID_STATUS_TRANSITIONS.get(self.status, []):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")

        old_status = self.status
        self.status = new_status
        self.modified_at = datetime.utcnow().isoformat()

        if new_status == 'posted':
            self.posted_at = datetime.utcnow().isoformat()
        elif new_status == 'void':
            if not void_reason:
                raise ValueError(
                    "Void reason is required when voiding a transaction")
            self.voided_at = datetime.utcnow().isoformat()
            self.void_reason = void_reason

    def post(self):
        """Post the transaction, changing its status to posted and updating account balances"""
        if self.status != 'draft':
            raise ValueError(f"Cannot post transaction with status '{self.status}'. Transaction must be in 'draft' status.")

        if self.posted_at:  # Check if transaction was already posted before
            raise ValueError("Transaction was already posted before")

        # Update account balances first
        self._update_account_balances()

        # If balance updates succeed, update status
        self.update_status('posted')
        self.posted_at = datetime.utcnow().isoformat()
        # Clear any void info since we're posting
        self.voided_at = None
        self.void_reason = None

    def void(self, void_reason: str = None):
        """Void the transaction and reverse its effect on account balances"""
        if void_reason is None or void_reason.strip() == "":
            raise ValueError("Void reason is required")

        # Only reverse balances if the transaction was posted
        if self.status == 'posted':
            self._reverse_account_balances()

        self.update_status('void', void_reason)
        self.void_reason = void_reason
        self.voided_at = datetime.utcnow().isoformat()

    def to_dict(self, for_appwrite: bool = False) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        # Convert entries to list of dictionaries
        entry_dicts = [entry.to_dict() for entry in self.entries]

        # For Appwrite, convert entries to JSON string
        if for_appwrite:
            entry_dicts = json.dumps(entry_dicts)

        data = {
            'user_id': self.user_id,
            'transaction_id': self.transaction_id,
            'transaction_date': self.transaction_date,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'total_amount': self.total_amount,
            'notes': self.notes,
            'entries': entry_dicts,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'posted_at': self.posted_at,
            'voided_at': self.voided_at,
            'void_reason': self.void_reason
        }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary"""
        # Remove Appwrite-specific fields if they exist
        appwrite_fields = ['$id', '$createdAt', '$updatedAt',
                           '$permissions', '$collectionId', '$databaseId']
        clean_data = {k: v for k,
                      v in data.items() if k not in appwrite_fields}

        transaction = cls(
            user_id=clean_data.get('user_id', ''),
            transaction_id=clean_data.get('transaction_id', ''),
            description=clean_data.get('description', ''),
            type=clean_data.get('type', 'journal_entry'),
            status=clean_data.get('status', 'draft'),
            notes=clean_data.get('notes'),
            created_at=clean_data.get(
                'created_at', datetime.utcnow().isoformat()),
            modified_at=clean_data.get(
                'modified_at', datetime.utcnow().isoformat()),
            posted_at=clean_data.get('posted_at'),
            voided_at=clean_data.get('voided_at'),
            void_reason=clean_data.get('void_reason')
        )

        # Handle entries - could be string or list
        entries_data = clean_data.get('entries', [])
        if isinstance(entries_data, str):
            try:
                entries_data = json.loads(entries_data)
            except json.JSONDecodeError:
                entries_data = []

        if entries_data:
            transaction.entries = [TransactionEntry.from_dict(
                entry) for entry in entries_data]
            transaction._calculate_total()

        return transaction

    @classmethod
    def _validate_accounts(cls, user_id: str, entries: List['TransactionEntry']) -> None:
        """
        Validate that all accounts in the transaction entries exist and belong to the user

        Args:
            user_id: ID of the user creating the transaction
            entries: List of transaction entries to validate

        Raises:
            ValueError: If any account doesn't exist or doesn't belong to the user
        """

        for entry in entries:
            # Try to get the account and verify ownership
            account = Account.get_account_by_id(entry.account_id, user_id)
            if not account:
                raise ValueError(
                    f"Account {entry.account_id} does not exist or does not belong to the user")
            if not account.is_active:
                raise ValueError(
                    f"Account {entry.account_id} is inactive and cannot be used in transactions")

    @classmethod
    def create_transaction(cls, user_id: str, description: str, entries: List['TransactionEntry'],
                           transaction_type: str = 'journal_entry', notes: Optional[str] = None):
        """Create a new transaction"""
        # Validate accounts first
        cls._validate_accounts(user_id, entries)

        # Generate a unique transaction ID
        transaction_id = cls.generate_transaction_id()

        # Create the transaction instance
        transaction = cls(
            user_id=user_id,
            transaction_id=transaction_id,
            description=description,
            type=transaction_type,
            notes=notes,
            entries=entries
        )

        # Add entries and validate
        transaction._validate_entries()
        transaction._calculate_total()

        return transaction

    @classmethod
    def get_database(cls) -> Databases:
        """Get Appwrite database instance"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)

    def _update_account_balances(self) -> None:
        """
        Update account balances based on transaction entries.
        Called when a transaction is posted.
        """
        from app.chart_of_accounts.models import Account

        # First verify all accounts exist and belong to user
        accounts_to_update = {}
        for entry in self.entries:
            try:
                account = Account.get_account_by_id(
                    entry.account_id, self.user_id)
                accounts_to_update[entry.account_id] = {
                    'account': account,
                    'balance_change': entry.debit_amount - entry.credit_amount
                }
            except ValueError as e:
                raise ValueError(f"Invalid account in transaction: {str(e)}")

        # Now update all account balances
        try:
            for account_id, update_info in accounts_to_update.items():
                account = update_info['account']
                balance_change = update_info['balance_change']

                # Only update the current balance and updated_at
                update_data = {
                    'current_balance': account.current_balance + balance_change,
                    'updated_at': datetime.utcnow().isoformat()
                }

                # Save to database using update_account
                Account.update_account(
                    account_id=account.account_id,
                    user_id=self.user_id,
                    data=update_data
                )

        except Exception as e:
            # If any update fails, we should ideally roll back previous updates
            # For now, just raise the error
            raise ValueError(f"Failed to update account balances: {str(e)}")

    def _reverse_account_balances(self) -> None:
        """
        Reverse the account balance updates from this transaction.
        Called when a transaction is voided.
        """
        from app.chart_of_accounts.models import Account

        # First verify all accounts exist and belong to user
        accounts_to_update = {}
        for entry in self.entries:
            try:
                account = Account.get_account_by_id(
                    entry.account_id, self.user_id)
                # Note: We reverse the balance change by negating it
                accounts_to_update[entry.account_id] = {
                    'account': account,
                    'balance_change': -(entry.debit_amount - entry.credit_amount)
                }
            except ValueError as e:
                raise ValueError(f"Invalid account in transaction: {str(e)}")

        # Now update all account balances
        try:
            for account_id, update_info in accounts_to_update.items():
                account = update_info['account']
                balance_change = update_info['balance_change']

                # Only update the current balance and updated_at
                update_data = {
                    'current_balance': account.current_balance + balance_change,
                    'updated_at': datetime.utcnow().isoformat()
                }

                # Save to database using update_account
                Account.update_account(
                    account_id=account.account_id,
                    user_id=self.user_id,
                    data=update_data
                )

        except Exception as e:
            # If any update fails, we should ideally roll back previous updates
            # For now, just raise the error
            raise ValueError(f"Failed to reverse account balances: {str(e)}")

    def _validate_account_types(self) -> None:
        """
        Validate that the account types used in the transaction entries match
        the allowed types for the transaction type.

        Raises:
            ValueError: If account types don't match the allowed types for the transaction
        """
        if not self.type in TRANSACTION_ACCOUNT_MAPPING:
            raise ValueError(f"Invalid transaction type: {self.type}")

        mapping = TRANSACTION_ACCOUNT_MAPPING[self.type]
        allowed_debit_types = mapping['debit']
        allowed_credit_types = mapping['credit']

        # Get all accounts used in the transaction
        account_ids = [entry.account_id for entry in self.entries]
        accounts = Account.get_accounts_by_ids(account_ids, self.user_id)

        # Create a mapping of account_id to account details for quick lookup
        account_info = {acc.account_id: (
            acc.account_type, acc.account_subtype) for acc in accounts}

        # Check each entry
        for entry in self.entries:
            if entry.account_id not in account_info:
                raise ValueError(f"Account {entry.account_id} not found")

            account_type, account_subtype = account_info[entry.account_id]

            # For entries with debit amount
            if entry.debit_amount > 0:
                if '*' not in allowed_debit_types and account_type not in allowed_debit_types:
                    allowed_types_str = ", ".join(allowed_debit_types)
                    raise ValueError(
                        f"Invalid account type for debit in {self.type} transaction. "
                        f"Account {entry.account_id} is of type {account_type}, "
                        f"but must be one of: {allowed_types_str}"
                    )

            # For entries with credit amount
            if entry.credit_amount > 0:
                if '*' not in allowed_credit_types and account_type not in allowed_credit_types:
                    allowed_types_str = ", ".join(allowed_credit_types)
                    raise ValueError(
                        f"Invalid account type for credit in {self.type} transaction. "
                        f"Account {entry.account_id} is of type {account_type}, "
                        f"but must be one of: {allowed_types_str}"
                    )

    def _validate_detail_types(self) -> None:
        """
        Validate that the account detail types used in the transaction entries match
        the allowed detail types for the transaction type.

        Raises:
            ValueError: If detail types don't match the allowed types for the transaction
        """
        if not self.type in TRANSACTION_DETAIL_TYPE_MAPPING:
            return  # Skip validation if no detail type mapping exists

        mapping = TRANSACTION_DETAIL_TYPE_MAPPING[self.type]
        allowed_debit_types = mapping['debit']
        allowed_credit_types = mapping['credit']

        # Get all accounts used in the transaction
        account_ids = [entry.account_id for entry in self.entries]
        accounts = Account.get_accounts_by_ids(account_ids, self.user_id)

        # Create a mapping of account_id to detail type for quick lookup
        account_subtypes = {
            acc.account_id: acc.account_subtype for acc in accounts}

        # Check each entry
        for entry in self.entries:
            detail_type = account_subtypes.get(entry.account_id)
            if not detail_type:
                raise ValueError(f"Account {entry.account_id} not found")

            # For entries with debit amount
            if entry.debit_amount > 0:
                if '*' not in allowed_debit_types and detail_type not in allowed_debit_types:
                    allowed_types_str = ", ".join(allowed_debit_types)
                    raise ValueError(
                        f"Invalid detail type for debit in {self.type} transaction. "
                        f"Account {entry.account_id} has detail type {detail_type}, "
                        f"but must be one of: {allowed_types_str}"
                    )

            # For entries with credit amount
            if entry.credit_amount > 0:
                if '*' not in allowed_credit_types and detail_type not in allowed_credit_types:
                    allowed_types_str = ", ".join(allowed_credit_types)
                    raise ValueError(
                        f"Invalid detail type for credit in {self.type} transaction. "
                        f"Account {entry.account_id} has detail type {detail_type}, "
                        f"but must be one of: {allowed_types_str}"
                    )

    def _validate_entries(self):
        """
        Validate all transaction entries:
        1. Ensure debits equal credits
        2. Ensure account types match transaction type
        3. Ensure detail types match transaction type
        """
        if not self.entries:
            return

        total_debits = sum(entry.debit_amount for entry in self.entries)
        total_credits = sum(entry.credit_amount for entry in self.entries)

        if abs(total_debits - total_credits) > 0.001:  # Using small epsilon for float comparison
            raise ValueError(
                f"Transaction entries must balance. Total debits ({total_debits}) "
                f"must equal total credits ({total_credits})"
            )

        # Validate both account types and detail types
        self._validate_account_types()
        self._validate_detail_types()

    def _calculate_total(self):
        """Calculate total amount from entries"""
        if not self.entries:
            self.total_amount = 0
            return
        # Use debit amounts for total since in double-entry both sides are equal
        self.total_amount = sum(entry.debit_amount for entry in self.entries)
