from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
import sys
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_models.default_coa import DEFAULT_ACCOUNTS
from app.data_models.coa_types import ACCOUNT_TYPE, DETAILS_TYPE

# Define the valid detail types for each account type
# ACCOUNT_TYPE_DETAILS = {
#     "Bank": ["Cash on hand", "Checking", "Money Market", "Rents Held in Trust", "Savings", "Trust account"],
#     "Accounts Receivable": ["Accounts Receivable"],
#     "Other Current Asset": [
#         "Allowance for Bad Debts",
#         "Development Costs",
#         "Employee Cash Advances",
#         "Inventory",
#         "Investment - Mortgage/Real Estate Loans",
#         "Investment - Tax-Exempt Securities",
#         "Investment - U.S. Government Obligations",
#         "Investments - Other",
#         "Loans To Officers",
#         "Loans to Others",
#         "Loans to Stockholders",
#         "Other Current Assets",
#         "Prepaid Expenses",
#         "Retainage",
#         "Undeposited Funds"
#     ],
#     "Fixed Asset": [
#         "Accumulated Amortization",
#         "Accumulated Depletion",
#         "Accumulated Depreciation",
#         "Buildings",
#         "Depletable Assets",
#         "Fixed Asset Computers",
#         "Fixed Asset Copiers",
#         "Fixed Asset Furniture",
#         "Fixed Asset Other Tools Equipment",
#         "Fixed Asset Phone",
#         "Fixed Asset Photo Video",
#         "Fixed Asset Software",
#         "Furniture & Fixtures",
#         "Intangible Assets",
#         "Land",
#         "Leasehold Improvements",
#         "Machinery & Equipment",
#         "Other fixed assets",
#         "Vehicles"
#     ],
#     "Other Asset": [
#         "Accumulated Amortization of Other Assets",
#         "Goodwill",
#         "Lease Buyout",
#         "Licenses",
#         "Organizational Costs",
#         "Other Long-term Assets",
#         "Security Deposits"
#     ],
#     "Accounts Payable": ["Accounts Payable"],
#     "Credit Card": ["Credit Card"],
#     "Other Current Liability": [
#         "Deferred Revenue",
#         "Federal Income Tax Payable",
#         "Insurance Payable",
#         "Line of Credit",
#         "Loan Payable",
#         "Other Current Liabilities",
#         "Payroll Clearing",
#         "Payroll Tax Payable",
#         "Prepaid Expenses Payable",
#         "Rents in trust - Liability",
#         "Sales Tax Payable",
#         "State/Local Income Tax Payable",
#         "Trust Accounts - Liabilities",
#         "Undistributed Tips"
#     ],
#     "Long Term Liabilities": [
#         "Notes Payable",
#         "Other Long Term Liabilities",
#         "Shareholder Notes Payable"
#     ],
#     "Equity": [
#         "Accumulated Adjustment",
#         "Common Stock",
#         "Estimated Taxes",
#         "Health Insurance Premium",
#         "Health Savings Account Contribution",
#         "Opening Balance Equity",
#         "Owner's Equity",
#         "Paid-In Capital or Surplus",
#         "Partner Contributions",
#         "Partner Distributions",
#         "Partner's Equity",
#         "Personal Expense",
#         "Personal Income",
#         "Preferred Stock",
#         "Retained Earnings",
#         "Treasury Stock"
#     ],
#     "Income": [
#         "Discounts/Refunds Given",
#         "Non-Profit Income",
#         "Other Primary Income",
#         "Sales of Product Income",
#         "Service/Fee Income",
#         "Unapplied Cash Payment Income"
#     ],
#     "Other Income": [
#         "Dividend Income",
#         "Interest Earned",
#         "Other Investment Income",
#         "Other Miscellaneous Income",
#         "Tax-Exempt Interest"
#     ],
#     "Cost of Goods Sold": [
#         "Cost of labor - COS",
#         "Equipment Rental - COS",
#         "Other Costs of Services - COS",
#         "Shipping, Freight & Delivery - COS",
#         "Supplies & Materials - COGS"
#     ],
#     "Expense": [
#         "Advertising/Promotional",
#         "Auto",
#         "Bad Debts",
#         "Bank Charges",
#         "Charitable Contributions",
#         "Communication",
#         "Cost of Labor",
#         "Dues & subscriptions",
#         "Entertainment",
#         "Entertainment Meals",
#         "Equipment Rental",
#         "Finance costs",
#         "Insurance",
#         "Interest Paid",
#         "Legal & Professional Fees",
#         "Office/General Administrative Expenses",
#         "Other Business Expenses",
#         "Other Miscellaneous Service Cost",
#         "Payroll Expenses",
#         "Payroll Tax Expenses",
#         "Payroll Wage Expenses",
#         "Promotional Meals",
#         "Rent or Lease of Buildings",
#         "Repair & Maintenance",
#         "Shipping, Freight & Delivery",
#         "Supplies & Materials",
#         "Taxes Paid",
#         "Travel",
#         "Travel Meals",
#         "Unapplied Cash Bill Payment Expense",
#         "Utilities"
#     ],
#     "Other Expense": [
#         "Amortization",
#         "Depreciation",
#         "Exchange Gain or Loss",
#         "Gas And Fuel",
#         "Home Office",
#         "Homeowner Rental Insurance",
#         "Mortgage Interest Home Office",
#         "Other Home Office Expenses",
#         "Other Miscellaneous Expense",
#         "Other Vehicle Expenses",
#         "Parking and Tolls",
#         "Penalties & Settlements",
#         "Property Tax Home Office",
#         "Rent and Lease Home Office",
#         "Repairs and Maintenance Home Office",
#         "Utilities Home Office",
#         "Vehicle",
#         "Vehicle Insurance",
#         "Vehicle Lease",
#         "Vehicle Loan",
#         "Vehicle Loan Interest",
#         "Vehicle Registration",
#         "Vehicle Repairs",
#         "Wash and Road Services"
#     ]
# }

# Default accounts that will be created for every new user
# DEFAULT_ACCOUNTS = [
#     # Asset Accounts (1000-1999)
#     {
#         "account_name": "Cash",
#         "account_type": "Bank",
#         "account_subtype": "Cash on hand",
#         "account_number": "1000",
#         "description": "Tracks cash on hand and in bank accounts"
#     },
#     {
#         "account_name": "Accounts Receivable",
#         "account_type": "Accounts Receivable",
#         "account_subtype": "Accounts Receivable (A/R)",
#         "account_number": "1100",
#         "description": "Records amounts owed by customers"
#     },
#     {
#         "account_name": "Inventory",
#         "account_type": "Other Current Asset",
#         "account_subtype": "Inventory",
#         "account_number": "1200",
#         "description": "Tracks goods held for sale"
#     },
#     {
#         "account_name": "Prepaid Expenses",
#         "account_type": "Other Current Asset",
#         "account_subtype": "Prepaid Expenses",
#         "account_number": "1300",
#         "description": "For expenses paid in advance (e.g., insurance, rent)"
#     },
#     {
#         "account_name": "Property, Plant, and Equipment",
#         "account_type": "Fixed Asset",
#         "account_subtype": "Other fixed assets",
#         "account_number": "1500",
#         "description": "Long-term assets like machinery or buildings"
#     },
#     {
#         "account_name": "Accumulated Depreciation",
#         "account_type": "Fixed Asset",
#         "account_subtype": "Accumulated Depreciation",
#         "account_number": "1600",
#         "description": "Contra-account to offset depreciation of PP&E"
#     },

#     # Liability Accounts (2000-2999)
#     {
#         "account_name": "Accounts Payable",
#         "account_type": "Accounts payable",
#         "account_subtype": "Accounts Payable",
#         "account_number": "2000",
#         "description": "Records amounts owed to suppliers/vendors"
#     },
#     {
#         "account_name": "Short-term Loans",
#         "account_type": "Other Current Liability",
#         "account_subtype": "Loan Payable",
#         "account_number": "2100",
#         "description": "Tracks outstanding short-term debt"
#     },
#     {
#         "account_name": "Long-term Loans",
#         "account_type": "Long Term Liabilities",
#         "account_subtype": "Notes Payable",
#         "account_number": "2200",
#         "description": "Tracks outstanding long-term debt"
#     },
#     {
#         "account_name": "Wages Payable",
#         "account_type": "Other Current Liability",
#         "account_subtype": "Payroll Tax Payable",
#         "account_number": "2300",
#         "description": "Unpaid wages due to employees"
#     },
#     {
#         "account_name": "Sales Tax Payable",
#         "account_type": "Other Current Liability",
#         "account_subtype": "Sales Tax Payable",
#         "account_number": "2400",
#         "description": "Taxes collected from customers to remit to authorities"
#     },
#     {
#         "account_name": "Unearned Revenue",
#         "account_type": "Other Current Liability",
#         "account_subtype": "Deferred Revenue",
#         "account_number": "2500",
#         "description": "Payments received for services/products not yet delivered"
#     },

#     # Equity Accounts (3000-3999)
#     {
#         "account_name": "Owner's Capital",
#         "account_type": "Equity",
#         "account_subtype": "Opening Balance Equity",
#         "account_number": "3000",
#         "description": "Initial investments by owners or shareholders"
#     },
#     {
#         "account_name": "Retained Earnings",
#         "account_type": "Equity",
#         "account_subtype": "Retained Earnings",
#         "account_number": "3100",
#         "description": "Cumulative profits reinvested in the business"
#     },
#     {
#         "account_name": "Owner's Draw",
#         "account_type": "Equity",
#         "account_subtype": "Owner's Equity",
#         "account_number": "3200",
#         "description": "Distributions to owners or shareholders"
#     },

#     # Revenue Accounts (4000-4999)
#     {
#         "account_name": "Sales Revenue",
#         "account_type": "Income",
#         "account_subtype": "Sales of Product Income",
#         "account_number": "4000",
#         "description": "Income from product sales"
#     },
#     {
#         "account_name": "Service Revenue",
#         "account_type": "Income",
#         "account_subtype": "Service/Fee Income",
#         "account_number": "4100",
#         "description": "Income from providing services"
#     },
#     {
#         "account_name": "Interest Income",
#         "account_type": "Other Income",
#         "account_subtype": "Interest Earned",
#         "account_number": "4200",
#         "description": "Earnings from investments or savings"
#     },

#     # Expense Accounts (5000-5999)
#     {
#         "account_name": "Cost of Goods Sold",
#         "account_type": "Cost of Goods Sold",
#         "account_subtype": "Supplies & Materials - COGS",
#         "account_number": "5000",
#         "description": "Direct costs of producing goods"
#     },
#     {
#         "account_name": "Rent Expense",
#         "account_type": "Expense",
#         "account_subtype": "Rent or Lease of Buildings",
#         "account_number": "5100",
#         "description": "Cost of leased premises"
#     },
#     {
#         "account_name": "Salaries and Wages",
#         "account_type": "Expense",
#         "account_subtype": "Payroll Wage Expenses",
#         "account_number": "5200",
#         "description": "Employee compensation"
#     },
#     {
#         "account_name": "Utilities",
#         "account_type": "Expense",
#         "account_subtype": "Utilities",
#         "account_number": "5300",
#         "description": "Electricity, water, internet, etc."
#     },
#     {
#         "account_name": "Office Supplies",
#         "account_type": "Expense",
#         "account_subtype": "Supplies & Materials",
#         "account_number": "5400",
#         "description": "Day-to-day operational supplies"
#     },
#     {
#         "account_name": "Depreciation Expense",
#         "account_type": "Other Expense",
#         "account_subtype": "Depreciation",
#         "account_number": "5500",
#         "description": "Allocation of asset costs over time"
#     },
#     {
#         "account_name": "Advertising and Marketing",
#         "account_type": "Expense",
#         "account_subtype": "Advertising/Promotional",
#         "account_number": "5600",
#         "description": "Promotional costs"
#     },
#     {
#         "account_name": "Interest Expense",
#         "account_type": "Expense",
#         "account_subtype": "Interest Paid",
#         "account_number": "5700",
#         "description": "Costs of borrowing funds"
#     },
#     {
#         "account_name": "Income Tax Expense",
#         "account_type": "Expense",
#         "account_subtype": "Taxes Paid",
#         "account_number": "5800",
#         "description": "Taxes on business profits"
#     }
# ]


@dataclass
class Account:
    """Represents an account in the Chart of Accounts"""
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "chart_of_accounts"

    # Required fields first
    user_id: str
    account_id: str
    account_name: str
    account_type: str
    account_subtype: str
    account_number: str

    # Optional fields with defaults
    description: Optional[str] = None
    is_active: bool = True
    opening_balance: float = 0.0
    current_balance: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())
    document_id: Optional[str] = None

    def __post_init__(self):
        """Validate the account after initialization"""
        if self.account_type not in ACCOUNT_TYPE:
            raise ValueError(f"Invalid account type: {self.account_type}")
        if self.account_subtype not in DETAILS_TYPE[self.account_type]:
            raise ValueError(
                f"Invalid account subtype for {self.account_type}: {self.account_subtype}")

    def to_dict(self, for_appwrite: bool = False) -> Dict[str, Any]:
        """Convert account to dictionary"""
        data = {
            "user_id": self.user_id,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "account_subtype": self.account_subtype,
            "account_number": self.account_number,
            "description": self.description,
            "is_active": self.is_active,
            "opening_balance": self.opening_balance,
            "current_balance": self.current_balance,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "document_id": self.document_id
        }

        if not for_appwrite:
            return data

        # Remove None values for Appwrite
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """Create account from dictionary"""
        # Store document_id from Appwrite's $id field
        document_id = data.get('$id')

        # Required fields with their default values
        required_fields = {
            'user_id': data.get('user_id', ''),
            'account_id': data.get('account_id', ID.unique()),
            'account_name': data.get('account_name', ''),
            'account_type': data.get('account_type', ''),
            'account_subtype': data.get('account_subtype', ''),
            'account_number': data.get('account_number', ''),
            'description': data.get('description', None),
            'is_active': data.get('is_active', True),
            'opening_balance': float(data.get('opening_balance', 0.0)),
            'current_balance': float(data.get('current_balance', 0.0)),
            'created_at': data.get('created_at', datetime.utcnow().isoformat()),
            'updated_at': data.get('updated_at', datetime.utcnow().isoformat())
        }

        # Add document_id if it exists
        if document_id:
            required_fields['document_id'] = document_id

        return cls(**required_fields)

    @staticmethod
    def generate_account_id() -> str:
        """Generate a random account ID with ACC prefix"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"ACC{first_half}-{second_half}"
            return id

    @classmethod
    def create_account(cls,
                       user_id: str,
                       account_name: str,
                       account_type: str,
                       account_subtype: str,
                       account_number: str,
                       description: Optional[str] = None,
                       opening_balance: float = 0.0) -> 'Account':
        """Create a new account"""
        try:
            # Make account number unique per user
            unique_account_number = f"{user_id}-{account_number}"

            # Create the account instance
            account = cls(
                user_id=user_id,
                account_id=cls.generate_account_id(),  # Use Appwrite's unique ID generator
                account_name=account_name,
                account_type=account_type,
                account_subtype=account_subtype,
                account_number=unique_account_number,  # Use the unique account number
                description=description,
                opening_balance=opening_balance,
                current_balance=opening_balance
            )

            # Save to database
            database = cls.get_database()
            try:
                data = account.to_dict(for_appwrite=True)
                result = database.create_document(
                    database_id=cls.DATABASE_ID,
                    collection_id=cls.COLLECTION_ID,
                    document_id=account.account_id,  # Use the generated account_id
                    data=data
                )
                # Return new instance with document_id from result
                return cls.from_dict(result)
            except Exception as db_error:
                raise Exception(
                    f"Database error creating account: {str(db_error)}")

        except ValueError as validation_error:
            raise Exception(f"Validation error: {str(validation_error)}")
        except Exception as e:
            raise Exception(f"Unexpected error creating account: {str(e)}")

    @classmethod
    def get_database(cls) -> Databases:
        """Get Appwrite database instance"""
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)

    @classmethod
    def get_account_by_id(cls, account_id: str, user_id: Optional[str] = None) -> 'Account':
        """Get an account by ID, optionally verifying ownership"""
        database = cls.get_database()
        try:
            result = database.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('account_id', account_id)]
            )

            if not result['documents']:
                raise ValueError(f"Account not found: {account_id}")

            account = cls.from_dict(result['documents'][0])

            if user_id and account.user_id != user_id:
                raise ValueError("Account does not belong to user")

            return account
        except Exception as e:
            raise Exception(f"Error retrieving account: {str(e)}")

    @classmethod
    def get_accounts_by_user(cls, user_id: str) -> List['Account']:
        """Get all accounts for a user"""
        database = cls.get_database()
        try:
            result = database.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.limit(100)
                    ]
            )
            return [cls.from_dict(doc) for doc in result['documents']]
        except Exception as e:
            raise Exception(f"Error retrieving accounts: {str(e)}")

    @classmethod
    def get_accounts_by_ids(cls, account_ids: List[str], user_id: str) -> List['Account']:
        """
        Get multiple accounts by their IDs, verifying they belong to the user

        Args:
            account_ids: List of account IDs to retrieve
            user_id: ID of the user who should own these accounts

        Returns:
            List of Account objects

        Raises:
            ValueError: If any account is not found or doesn't belong to the user
        """
        if not account_ids:
            return []

        database = cls.get_database()

        # Query for all accounts that match the IDs and user_id
        result = database.list_documents(
            database_id=cls.DATABASE_ID,
            collection_id=cls.COLLECTION_ID,
            queries=[
                Query.equal('user_id', user_id),
                Query.equal('account_id', account_ids)
            ]
        )

        # Convert results to Account objects
        accounts = [cls.from_dict(doc) for doc in result['documents']]

        # Verify we found all requested accounts
        found_ids = {acc.account_id for acc in accounts}
        missing_ids = set(account_ids) - found_ids

        if missing_ids:
            raise ValueError(
                f"Could not find accounts with IDs: {', '.join(missing_ids)}")

        return accounts

    @classmethod
    def update_account(cls, account_id: str, user_id: str, data: Dict) -> 'Account':
        """Update an account, verifying ownership first"""
        # Get existing account to verify ownership and get document_id
        existing = cls.get_account_by_id(account_id, user_id)
        if not existing.document_id:
            raise ValueError("Account document_id not found")

        database = cls.get_database()
        try:
            # Add updated timestamp
            data['updated_at'] = datetime.utcnow().isoformat()

            # Update in database using document_id
            result = database.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=existing.document_id,  # Use document_id instead of account_id
                data=data
            )
            return cls.from_dict(result)
        except Exception as e:
            raise Exception(f"Error updating account: {str(e)}")

    @classmethod
    def delete_account(cls, account_id: str, user_id: str) -> bool:
        """Delete an account, verifying ownership first"""
        # Get existing account to verify ownership and get document_id
        existing = cls.get_account_by_id(account_id, user_id)
        if not existing.document_id:
            raise ValueError("Account document_id not found")

        database = cls.get_database()
        try:
            # Delete using document_id
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=existing.document_id  # Use document_id instead of account_id
            )
            return True
        except Exception as e:
            raise Exception(f"Error deleting account: {str(e)}")

    @classmethod
    def delete_all_accounts_for_user(cls, user_id: str) -> int:
        """Delete all accounts for a user at once

        Args:
            user_id: The ID of the user whose accounts should be deleted

        Returns:
            int: Number of accounts deleted

        Raises:
            Exception: If there was an error deleting the accounts
        """
        database = cls.get_database()
        try:
            # First get all account documents for the user
            result = database.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )

            deleted_count = 0
            for doc in result['documents']:
                try:
                    database.delete_document(
                        database_id=cls.DATABASE_ID,
                        collection_id=cls.COLLECTION_ID,
                        document_id=doc['$id']
                    )
                    deleted_count += 1
                except Exception as e:
                    # Log the error but continue with other deletions
                    print(f"Error deleting account {doc['$id']}: {str(e)}")

            return deleted_count

        except Exception as e:
            raise Exception(f"Error deleting accounts for user: {str(e)}")

    @classmethod
    def create_default_accounts(cls, user_id: str) -> List['Account']:
        """Create default accounts for a new user"""
        created_accounts = []
        for account_data in DEFAULT_ACCOUNTS:
            try:
                account = cls.create_account(
                    user_id=user_id,
                    account_name=account_data["account_name"],
                    account_type=account_data["account_type"],
                    account_subtype=account_data["account_subtype"],
                    account_number=account_data["account_number"],
                    description=account_data["description"]
                )
                created_accounts.append(account)
            except Exception as e:
                # Log error but continue creating other accounts
                print(
                    f"Error creating default account {account_data['account_name']}: {str(e)}")
                continue
        return created_accounts
