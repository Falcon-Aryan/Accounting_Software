from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import os

# Define the valid detail types for each account type
ACCOUNT_TYPE_DETAILS = {
    "Bank": ["Cash on hand", "Checking", "Money Market", "Rents Held in Trust", "Savings", "Trust account"],
    "Accounts Receivable": ["Accounts Receivable (A/R)"],
    "Other Current Asset": [
        "Allowance for Bad Debts",
        "Development Costs",
        "Employee Cash Advances",
        "Inventory",
        "Investment - Mortgage/Real Estate Loans",
        "Investment - Tax-Exempt Securities",
        "Investment - U.S. Government Obligations",
        "Investments - Other",
        "Loans To Officers",
        "Loans to Others",
        "Loans to Stockholders",
        "Other Current Assets",
        "Prepaid Expenses",
        "Retainage",
        "Undeposited Funds"
    ],
    "Fixed Asset": [
        "Accumulated Amortization",
        "Accumulated Depletion",
        "Accumulated Depreciation",
        "Buildings",
        "Depletable Assets",
        "Fixed Asset Computers",
        "Fixed Asset Copiers",
        "Fixed Asset Furniture",
        "Fixed Asset Other Tools Equipment",
        "Fixed Asset Phone",
        "Fixed Asset Photo Video",
        "Fixed Asset Software",
        "Furniture & Fixtures",
        "Intangible Assets",
        "Land",
        "Leasehold Improvements",
        "Machinery & Equipment",
        "Other fixed assets",
        "Vehicles"
    ],
    "Other Asset": [
        "Accumulated Amortization of Other Assets",
        "Goodwill",
        "Lease Buyout",
        "Licenses",
        "Organizational Costs",
        "Other Long-term Assets",
        "Security Deposits"
    ],
    "Accounts payable (A/P)": ["Accounts Payable (A/P)"],
    "Credit Card": ["Credit Card"],
    "Other Current Liability": [
        "Deferred Revenue",
        "Federal Income Tax Payable",
        "Insurance Payable",
        "Line of Credit",
        "Loan Payable",
        "Other Current Liabilities",
        "Payroll Clearing",
        "Payroll Tax Payable",
        "Prepaid Expenses Payable",
        "Rents in trust - Liability",
        "Sales Tax Payable",
        "State/Local Income Tax Payable",
        "Trust Accounts - Liabilities",
        "Undistributed Tips"
    ],
    "Long Term Liabilities": [
        "Notes Payable",
        "Other Long Term Liabilities",
        "Shareholder Notes Payable"
    ],
    "Equity": [
        "Accumulated Adjustment",
        "Common Stock",
        "Estimated Taxes",
        "Health Insurance Premium",
        "Health Savings Account Contribution",
        "Opening Balance Equity",
        "Owner's Equity",
        "Paid-In Capital or Surplus",
        "Partner Contributions",
        "Partner Distributions",
        "Partner's Equity",
        "Personal Expense",
        "Personal Income",
        "Preferred Stock",
        "Retained Earnings",
        "Treasury Stock"
    ],
    "Income": [
        "Discounts/Refunds Given",
        "Non-Profit Income",
        "Other Primary Income",
        "Sales of Product Income",
        "Service/Fee Income",
        "Unapplied Cash Payment Income"
    ],
    "Other Income": [
        "Dividend Income",
        "Interest Earned",
        "Other Investment Income",
        "Other Miscellaneous Income",
        "Tax-Exempt Interest"
    ],
    "Cost of Goods Sold": [
        "Cost of labor - COS",
        "Equipment Rental - COS",
        "Other Costs of Services - COS",
        "Shipping, Freight & Delivery - COS",
        "Supplies & Materials - COGS"
    ],
    "Expense": [
        "Advertising/Promotional",
        "Auto",
        "Bad Debts",
        "Bank Charges",
        "Charitable Contributions",
        "Communication",
        "Cost of Labor",
        "Dues & subscriptions",
        "Entertainment",
        "Entertainment Meals",
        "Equipment Rental",
        "Finance costs",
        "Insurance",
        "Interest Paid",
        "Legal & Professional Fees",
        "Office/General Administrative Expenses",
        "Other Business Expenses",
        "Other Miscellaneous Service Cost",
        "Payroll Expenses",
        "Payroll Tax Expenses",
        "Payroll Wage Expenses",
        "Promotional Meals",
        "Rent or Lease of Buildings",
        "Repair & Maintenance",
        "Shipping, Freight & Delivery",
        "Supplies & Materials",
        "Taxes Paid",
        "Travel",
        "Travel Meals",
        "Unapplied Cash Bill Payment Expense",
        "Utilities"
    ],
    "Other Expense": [
        "Amortization",
        "Depreciation",
        "Exchange Gain or Loss",
        "Gas And Fuel",
        "Home Office",
        "Homeowner Rental Insurance",
        "Mortgage Interest Home Office",
        "Other Home Office Expenses",
        "Other Miscellaneous Expense",
        "Other Vehicle Expenses",
        "Parking and Tolls",
        "Penalties & Settlements",
        "Property Tax Home Office",
        "Rent and Lease Home Office",
        "Repairs and Maintenance Home Office",
        "Utilities Home Office",
        "Vehicle",
        "Vehicle Insurance",
        "Vehicle Lease",
        "Vehicle Loan",
        "Vehicle Loan Interest",
        "Vehicle Registration",
        "Vehicle Repairs",
        "Wash and Road Services"
    ]
}

# Account type to normal balance mapping
NORMAL_BALANCE_TYPES = {
    "Asset": "debit",
    "Bank": "debit",
    "Accounts Receivable": "debit",
    "Other Current Asset": "debit",
    "Fixed Asset": "debit",
    "Other Asset": "debit",
    "Liability": "credit",
    "Accounts Payable": "credit",
    "Credit Card": "credit",
    "Other Current Liability": "credit",
    "Long Term Liability": "credit",
    "Other Liability": "credit",
    "Equity": "credit",
    "Income": "credit",
    "Other Income": "credit",
    "Cost of Goods Sold": "debit",
    "Expense": "debit",
    "Other Expense": "debit"
}

@dataclass
class Account:
    """Represents a Chart of Accounts entry"""
    id: str
    name: str
    accountType: str
    detailType: str
    description: Optional[str] = None
    openingBalance: float = 0.0
    currentBalance: float = 0.0
    normalBalanceType: str = None
    parentAccountId: Optional[str] = None
    lastTransactionDate: Optional[datetime] = None
    active: bool = True
    isDefault: bool = False

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @staticmethod
    def get_user_data_file(uid: str) -> str:
        """Get the path to the user's chart_of_accounts.json file"""
        return os.path.join(Account.BASE_DIR, 'data', uid, 'chart_of_accounts.json')

    @staticmethod
    def get_default_accounts_file() -> str:
        """Get the path to the default accounts template file"""
        return os.path.join(Account.BASE_DIR, 'data', 'defaults', 'default_accounts.json')

    def __post_init__(self):
        """Set the normal balance type based on account type"""
        if not self.normalBalanceType:
            self.normalBalanceType = NORMAL_BALANCE_TYPES.get(self.accountType, "debit")
        if self.currentBalance is None:
            self.currentBalance = self.openingBalance

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """Create an Account instance from a dictionary"""
        # Convert lastTransactionDate if it exists
        last_transaction = data.get('lastTransactionDate')
        if isinstance(last_transaction, str):
            last_transaction = datetime.fromisoformat(last_transaction.replace('Z', '+00:00'))

        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            accountType=data.get('accountType', ''),
            detailType=data.get('detailType', ''),
            description=data.get('description'),
            openingBalance=float(data.get('openingBalance', 0.0)),
            currentBalance=float(data.get('currentBalance', data.get('openingBalance', 0.0))),
            normalBalanceType=data.get('normalBalanceType'),
            parentAccountId=data.get('parentAccountId'),
            lastTransactionDate=last_transaction,
            active=data.get('active', True),
            isDefault=data.get('isDefault', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Account instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'accountType': self.accountType,
            'detailType': self.detailType,
            'description': self.description,
            'openingBalance': self.openingBalance,
            'currentBalance': self.currentBalance,
            'normalBalanceType': self.normalBalanceType,
            'parentAccountId': self.parentAccountId,
            'lastTransactionDate': self.lastTransactionDate.isoformat() if self.lastTransactionDate else None,
            'active': self.active,
            'isDefault': self.isDefault
        }

    def validate_transaction(self, amount: float, type: str) -> tuple[bool, Optional[str]]:
        """Validate if a transaction can be applied to this account"""
        if not self.active:
            return False, "Account is inactive"
        
        if type not in ['debit', 'credit']:
            return False, "Invalid transaction type"
        
        if amount <= 0:
            return False, "Amount must be positive"

        return True, None

    def calculate_balance_change(self, amount: float, type: str) -> float:
        """Calculate how a transaction will affect the balance"""
        if type == self.normalBalanceType:
            return amount
        return -amount

    def update_balance(self, amount: float, type: str) -> tuple[bool, Optional[str]]:
        """Update account balance based on transaction"""
        # Validate transaction first
        is_valid, error = self.validate_transaction(amount, type)
        if not is_valid:
            return False, error

        # Calculate balance change
        balance_change = self.calculate_balance_change(amount, type)
        
        # Update balance and last transaction date
        self.currentBalance += balance_change
        self.lastTransactionDate = datetime.utcnow()
        
        return True, None

@dataclass
class AccountsSummary:
    """
    Represents summary information for all accounts
    """
    totalAccounts: int = 0
    activeAccounts: int = 0
    inactiveAccounts: int = 0
    totalDebit: float = 0.0
    totalCredit: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountsSummary':
        """Create an AccountsSummary instance from a dictionary"""
        return cls(
            totalAccounts=data.get('totalAccounts', 0),
            activeAccounts=data.get('activeAccounts', 0),
            inactiveAccounts=data.get('inactiveAccounts', 0),
            totalDebit=data.get('totalDebit', 0.0),
            totalCredit=data.get('totalCredit', 0.0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert AccountsSummary instance to dictionary"""
        return {
            'totalAccounts': self.totalAccounts,
            'activeAccounts': self.activeAccounts,
            'inactiveAccounts': self.inactiveAccounts,
            'totalDebit': self.totalDebit,
            'totalCredit': self.totalCredit
        }