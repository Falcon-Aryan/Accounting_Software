TRANSACTION_STATUSES = [
    'draft',
    'posted',
    'void'
]

VALID_STATUS_TRANSITIONS = {
    'draft': ['posted', 'void'],
    'posted': ['void', 'draft'],
    'void': ['draft']
}

TRANSACTION_TYPES = [
    # Core Accounting Transactions
    'sales_invoice',          # Invoice
    'sales_receipt',          # SalesReceipt
    'payment',                # ReceivePayment
    'bill',                   # Bill (vendor invoice)
    'bill_payment',           # BillPaymentCheck/BillPaymentCreditCard
    'journal_entry',          # JournalEntry
    'transfer',               # Transfer
    'deposit',                # Deposit
    'charge',                 # Charge/CreditCardCharge
    'vendor_credit',          # VendorCredit
    'customer_credit',        # Credit/CreditMemo

    # Payment Methods
    'check',                  # Check
    'credit_card',           # CreditCardCharge/CreditCardCredit

    # Essential Business Operations
    'purchase_invoice',       # Bill
    'cash_purchase',          # CashPurchase
    'bank_deposit',           # Deposit
    'bank_withdrawal',        # Withdrawal

    # Basic Adjustments
    'inventory_adjustment',   # InventoryQuantityAdjustment
    'credit_refund',         # CreditRefund

    # General Expenses
    'general_expense',        # Expense
    'other_income',          # OtherIncome
    'other_expense',         # OtherExpense

    # Owner Transactions
    'owner_contribution',     # OwnerContribution
    'owner_drawing',         # OwnerDrawing

    # Other Essential Transactions
    'purchase_order',        # PurchaseOrder (important for inventory)
    'other_transaction'      # Miscellaneous entries
]


# Define valid account types for each transaction type
TRANSACTION_ACCOUNT_MAPPING = {

    # Core Accounting Transactions
    'sales_invoice': {
        'debit': {'Accounts Receivable'},
        'credit': {'Income', 'Other Income'}
    },
    'sales_receipt': {
        'debit': {'Bank', 'Other Current Asset'},
        'credit': {'Income', 'Other Income'}
    },
    'payment': {
        'debit': {'Bank', 'Other Current Asset'},
        'credit': {'Accounts Receivable'}
    },
    'bill': {
        'debit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Accounts Payable'}
    },
    'bill_payment': {
        'debit': {'Accounts Payable'},
        'credit': {'Bank', 'Credit Card', 'Other Current Asset'}
    },
    'journal_entry': {
        'debit': {'Bank', 'Accounts Receivable', 'Other Current Asset', 'Fixed Asset', 'Other Asset', 'Expense', 'Other Expense', 'Cost of Goods Sold'},
        'credit': {'Bank', 'Accounts Payable', 'Credit Card', 'Other Current Liability', 'Long Term Liabilities', 'Equity', 'Income', 'Other Income'}
    },
    'transfer': {
        'debit': {'Bank', 'Other Current Asset'},
        'credit': {'Bank', 'Other Current Asset'}
    },
    'deposit': {
        'debit': {'Bank'},
        'credit': {'Other Current Asset', 'Income', 'Other Income', 'Equity'}
    },
    'charge': {
        'debit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Credit Card'}
    },
    'vendor_credit': {
        'debit': {'Accounts Payable'},
        'credit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset'}
    },
    'customer_credit': {
        'debit': {'Income', 'Other Income'},
        'credit': {'Accounts Receivable', 'Bank'}
    },

    # Payment Methods
    'check': {
        'debit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Bank'}
    },
    'credit_card': {
        'debit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Credit Card'}
    },

    # Essential Business Operations
    'purchase_invoice': {
        'debit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Accounts Payable'}
    },
    'cash_purchase': {
        'debit': {'Expense', 'Other Expense', 'Cost of Goods Sold', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Bank'}
    },
    'bank_deposit': {
        'debit': {'Bank'},
        'credit': {'Other Current Asset', 'Income', 'Other Income', 'Equity'}
    },
    'bank_withdrawal': {
        'debit': {'Expense', 'Other Expense'},
        'credit': {'Bank'}
    },
    'general_expense': {
        'debit': {'Expense', 'Other Expense'},
        'credit': {'Bank', 'Credit Card', 'Other Current Asset'}
    },

    # Basic Adjustments
    'inventory_adjustment': {
        'debit': {'Other Current Asset', 'Cost of Goods Sold'},
        'credit': {'Other Current Asset', 'Cost of Goods Sold'}
    },
    'credit_refund': {
        'debit': {'Credit Card'},
        'credit': {'Expense', 'Other Expense', 'Other Current Asset'}
    },

    # General Expenses
    'other_income': {
        'debit': {'Bank', 'Other Current Asset'},
        'credit': {'Other Income'}
    },
    'other_expense': {
        'debit': {'Other Expense'},
        'credit': {'Bank', 'Credit Card', 'Other Current Asset'}
    },

    # Owner Transactions
    'owner_contribution': {
        'debit': {'Bank', 'Other Current Asset', 'Fixed Asset'},
        'credit': {'Equity'}
    },
    'owner_drawing': {
        'debit': {'Equity'},
        'credit': {'Bank', 'Other Current Asset'}
    },

    # Other Essential Transactions
    'purchase_order': {
        'debit': {'Other Current Asset'},
        'credit': {'Other Current Liability'}
    },
    'other_transaction': {
        'debit': {'Bank', 'Accounts Receivable', 'Other Current Asset', 'Fixed Asset', 'Other Asset', 'Expense', 'Other Expense'},
        'credit': {'Bank', 'Accounts Payable', 'Credit Card', 'Other Current Liability', 'Long Term Liabilities', 'Equity', 'Income', 'Other Income'}
    }
}

# Default detail types for automatic transactions
TRANSACTION_DETAIL_TYPE_MAPPING = {
    'sales_invoice': {
        'debit': ['Accounts Receivable'],
        'credit': ['Sales of Product Income', 'Service/Fee Income']
    },
    'sales_receipt': {
        'debit': ['Checking', 'Savings', 'Cash on hand'],
        'credit': ['Sales of Product Income', 'Service/Fee Income']
    },
    'payment': {
        'debit': ['Checking', 'Savings'],
        'credit': ['Accounts Payable']
    },
    'bill': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Other Business Expenses'
        ],
        'credit': ['Accounts Payable']
    },
    'bill_payment': {
        'debit': ['Accounts Payable'],
        'credit': ['Checking', 'Savings']
    },
    'transfer': {
        'debit': ['Checking', 'Savings', 'Money Market'],
        'credit': ['Checking', 'Savings', 'Money Market']
    },
    'deposit': {
        'debit': ['Checking', 'Savings'],
        'credit': ['Undeposited Funds', 'Other Primary Income']
    },
    'charge': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Travel',
            'Entertainment'
        ],
        'credit': ['Credit Card']
    },
    'vendor_credit': {
        'debit': ['Accounts Payable'],
        'credit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Other Business Expenses'
        ]
    },
    'customer_credit': {
        'debit': ['Sales of Product Income', 'Service/Fee Income'],
        'credit': ['Accounts Receivable']
    },
    'bank_withdrawal': {
        'debit': [
            'Office/General Administrative Expenses',
            'Other Business Expenses'
        ],
        'credit': ['Checking', 'Savings']
    },
    'general_expense': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Travel',
            'Entertainment',
            'Other Business Expenses'
        ],
        'credit': ['Checking', 'Savings', 'Credit Card']
    },
    'inventory_adjustment': {
        'debit': ['Inventory'],
        'credit': ['Supplies & Materials - COGS']
    },
    'owner_contribution': {
        'debit': ['Checking', 'Savings'],
        'credit': ['Owner\'s Equity']
    },
    'owner_drawing': {
        'debit': ['Owner\'s Equity'],
        'credit': ['Checking', 'Savings']
    },
    'check': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Other Business Expenses',
            'Travel',
            'Entertainment'
        ],
        'credit': ['Checking', 'Savings']
    },
    'credit_card': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Travel',
            'Entertainment',
            'Other Business Expenses'
        ],
        'credit': ['Credit Card']
    },
    'credit_refund': {
        'debit': ['Credit Card'],
        'credit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Other Business Expenses'
        ]
    },
    'other_income': {
        'debit': ['Checking', 'Savings', 'Undeposited Funds'],
        'credit': [
            'Other Investment Income',
            'Other Miscellaneous Income',
            'Interest Earned',
            'Dividend Income'
        ]
    },
    'other_expense': {
        'debit': [
            'Other Miscellaneous Expense',
            'Other Vehicle Expenses',
            'Other Home Office Expenses'
        ],
        'credit': ['Checking', 'Savings', 'Credit Card']
    },
    'journal_entry': {
        'debit': [
            'Checking', 'Savings', 'Accounts Receivable', 'Inventory',
            'Office/General Administrative Expenses', 'Supplies & Materials',
            'Other Business Expenses', 'Cost of labor - COS',
            'Equipment Rental - COS', 'Other Costs of Services - COS'
        ],
        'credit': [
            'Checking', 'Savings', 'Accounts Payable', 'Credit Card',
            'Sales of Product Income', 'Service/Fee Income',
            'Other Primary Income', 'Other Investment Income'
        ]
    },
    'purchase_invoice': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Other Business Expenses',
            'Cost of labor - COS',
            'Equipment Rental - COS',
            'Other Costs of Services - COS'
        ],
        'credit': ['Accounts Payable']
    },
    'cash_purchase': {
        'debit': [
            'Office/General Administrative Expenses',
            'Supplies & Materials',
            'Other Business Expenses',
            'Cost of labor - COS',
            'Equipment Rental - COS',
            'Other Costs of Services - COS'
        ],
        'credit': ['Checking', 'Savings', 'Cash on hand']
    },
    'bank_deposit': {
        'debit': ['Checking', 'Savings'],
        'credit': [
            'Undeposited Funds',
            'Other Primary Income',
            'Sales of Product Income',
            'Service/Fee Income'
        ]
    },
    'purchase_order': {
        'debit': ['Inventory'],
        'credit': [
            'Other Current Liabilities',
            'Loan Payable',
            'Line of Credit'
        ]
    },
    'other_transaction': {
        'debit': [
            'Checking', 'Savings', 'Accounts Receivable', 'Inventory',
            'Office/General Administrative Expenses', 'Other Business Expenses',
            'Cost of labor - COS', 'Equipment Rental - COS',
            'Other Costs of Services - COS', 'Supplies & Materials'
        ],
        'credit': [
            'Checking', 'Savings', 'Accounts Payable', 'Credit Card',
            'Sales of Product Income', 'Other Primary Income',
            'Service/Fee Income', 'Other Investment Income',
            'Other Current Liabilities', 'Loan Payable'
        ]
    }
}
