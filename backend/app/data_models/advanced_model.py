"""Advanced settings data model and constants"""

# Fiscal year start months
FISCAL_YEAR_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

# Accounting methods
ACCOUNTING_METHODS = [
    "Accrual",
    "Cash"
]

# Company tax forms
COMPANY_TAX_FORMS = [
    "Sole Proprietor (Form 1040)",
    "Partnership or limited liability company (Form 1065)",
    "Small Business corporation, two or more owners (Form 1120S)",
    "Corporation, one or more shareholders (Form 1120)",
    "Nonprofit organization (Form 990)",
    "Limited Liability",
    "Other (Please specify)"
]

# Date formats
DATE_FORMATS = [
    "MM/DD/YYYY",
    "DD/MM/YYYY",
    "YYYY/MM/DD",
    "MM-DD-YYYY",
    "DD-MM-YYYY",
    "YYYY-MM-DD"
]

# Currency formats
CURRENCY_FORMATS = [
    "$#,##0.00",
    "# ###,## $",
    "#.###,## €",
    "¥#,###",
    "£#,##0.00"
]

# Inactivity timeouts
INACTIVITY_TIMEOUTS = [
    "1 hour",
    "2 hours",
    "3 hours",
    "4 hours",
    "8 hours"
]

# Default settings
DEFAULT_SETTINGS = {
    "fiscal_year_start": "January",
    "income_tax_year_start": "Same as fiscal year",
    "accounting_method": "Accrual",
    "close_the_books": False,
    "tax_form": "Sole Proprietor (Form 1040)",
    "enable_account_numbers": True,
    "tips_account": "Cash on Hand",
    "track_classes": False,
    "track_locations": False,
    "pre_fill_forms": True,
    "apply_credits_automatically": True,
    "invoice_unbilled_activity": False,
    "apply_bill_payments_automatically": True,
    "organize_job_activity": False,
    "home_currency": "USD",
    "multicurrency": False,
    "date_format": "MM/DD/YYYY",
    "currency_format": "$#,##0.00",
    "customer_label": "Customer",
    "duplicate_check_warning": True,
    "vendor_bill_warning": True,
    "duplicate_journal_warning": True,
    "sign_out_after_inactivity": "3 hours"
}