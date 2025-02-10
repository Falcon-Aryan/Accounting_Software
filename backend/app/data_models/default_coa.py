DEFAULT_ACCOUNTS = [
    # Asset Accounts (1000-1999)
    {
        "account_name": "Cash",
        "account_type": "Bank",
        "account_subtype": "Cash on hand",
        "account_number": "1000",
        "description": "Tracks cash on hand and in bank accounts"
    },
    {
        "account_name": "Accounts Receivable",
        "account_type": "Accounts Receivable",
        "account_subtype": "Accounts Receivable",
        "account_number": "1100",
        "description": "Records amounts owed by customers"
    },
    {
        "account_name": "Inventory",
        "account_type": "Other Current Asset",
        "account_subtype": "Inventory",
        "account_number": "1200",
        "description": "Tracks goods held for sale"
    },
    {
        "account_name": "Prepaid Expenses",
        "account_type": "Other Current Asset",
        "account_subtype": "Prepaid Expenses",
        "account_number": "1300",
        "description": "For expenses paid in advance (e.g., insurance, rent)"
    },
    {
        "account_name": "Property, Plant, and Equipment",
        "account_type": "Fixed Asset",
        "account_subtype": "Other fixed assets",
        "account_number": "1500",
        "description": "Long-term assets like machinery or buildings"
    },
    {
        "account_name": "Accumulated Depreciation",
        "account_type": "Fixed Asset",
        "account_subtype": "Accumulated Depreciation",
        "account_number": "1600",
        "description": "Contra-account to offset depreciation of PP&E"
    },

    # Liability Accounts (2000-2999)
    {
        "account_name": "Accounts Payable",
        "account_type": "Accounts Payable",
        "account_subtype": "Accounts Payable",
        "account_number": "2000",
        "description": "Records amounts owed to suppliers/vendors"
    },
    {
        "account_name": "Short-term Loans",
        "account_type": "Other Current Liability",
        "account_subtype": "Loan Payable",
        "account_number": "2100",
        "description": "Tracks outstanding short-term debt"
    },
    {
        "account_name": "Long-term Loans",
        "account_type": "Long Term Liabilities",
        "account_subtype": "Notes Payable",
        "account_number": "2200",
        "description": "Tracks outstanding long-term debt"
    },
    {
        "account_name": "Wages Payable",
        "account_type": "Other Current Liability",
        "account_subtype": "Payroll Tax Payable",
        "account_number": "2300",
        "description": "Unpaid wages due to employees"
    },
    {
        "account_name": "Sales Tax Payable",
        "account_type": "Other Current Liability",
        "account_subtype": "Sales Tax Payable",
        "account_number": "2400",
        "description": "Taxes collected from customers to remit to authorities"
    },
    {
        "account_name": "Unearned Revenue",
        "account_type": "Other Current Liability",
        "account_subtype": "Deferred Revenue",
        "account_number": "2500",
        "description": "Payments received for services/products not yet delivered"
    },

    # Equity Accounts (3000-3999)
    {
        "account_name": "Owner's Capital",
        "account_type": "Equity",
        "account_subtype": "Opening Balance Equity",
        "account_number": "3000",
        "description": "Initial investments by owners or shareholders"
    },
    {
        "account_name": "Retained Earnings",
        "account_type": "Equity",
        "account_subtype": "Retained Earnings",
        "account_number": "3100",
        "description": "Cumulative profits reinvested in the business"
    },
    {
        "account_name": "Owner's Draw",
        "account_type": "Equity",
        "account_subtype": "Owner's Equity",
        "account_number": "3200",
        "description": "Distributions to owners or shareholders"
    },

    # Revenue Accounts (4000-4999)
    {
        "account_name": "Sales Revenue",
        "account_type": "Income",
        "account_subtype": "Sales of Product Income",
        "account_number": "4000",
        "description": "Income from product sales"
    },
    {
        "account_name": "Service Revenue",
        "account_type": "Income",
        "account_subtype": "Service/Fee Income",
        "account_number": "4100",
        "description": "Income from providing services"
    },
    {
        "account_name": "Interest Income",
        "account_type": "Other Income",
        "account_subtype": "Interest Earned",
        "account_number": "4200",
        "description": "Earnings from investments or savings"
    },

    # Expense Accounts (5000-5999)
    {
        "account_name": "Cost of Goods Sold",
        "account_type": "Cost of Goods Sold",
        "account_subtype": "Supplies & Materials - COGS",
        "account_number": "5000",
        "description": "Direct costs of producing goods"
    },
    {
        "account_name": "Rent Expense",
        "account_type": "Expense",
        "account_subtype": "Rent or Lease of Buildings",
        "account_number": "5100",
        "description": "Cost of leased premises"
    },
    {
        "account_name": "Salaries and Wages",
        "account_type": "Expense",
        "account_subtype": "Payroll Wage Expenses",
        "account_number": "5200",
        "description": "Employee compensation"
    },
    {
        "account_name": "Utilities",
        "account_type": "Expense",
        "account_subtype": "Utilities",
        "account_number": "5300",
        "description": "Electricity, water, internet, etc."
    },
    {
        "account_name": "Office Supplies",
        "account_type": "Expense",
        "account_subtype": "Supplies & Materials",
        "account_number": "5400",
        "description": "Day-to-day operational supplies"
    },
    {
        "account_name": "Depreciation Expense",
        "account_type": "Other Expense",
        "account_subtype": "Depreciation",
        "account_number": "5500",
        "description": "Allocation of asset costs over time"
    },
    {
        "account_name": "Advertising and Marketing",
        "account_type": "Expense",
        "account_subtype": "Advertising/Promotional",
        "account_number": "5600",
        "description": "Promotional costs"
    },
    {
        "account_name": "Interest Expense",
        "account_type": "Expense",
        "account_subtype": "Interest Paid",
        "account_number": "5700",
        "description": "Costs of borrowing funds"
    },
    {
        "account_name": "Income Tax Expense",
        "account_type": "Expense",
        "account_subtype": "Taxes Paid",
        "account_number": "5800",
        "description": "Taxes on business profits"
    }
]
