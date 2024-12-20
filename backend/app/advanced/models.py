from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Accounting:
    fiscal_year_start: str  # Month name
    income_tax_year_start: str
    accounting_method: str
    close_the_books: bool

@dataclass
class CompanyType:
    tax_form: str

@dataclass
class ChartOfAccounts:
    enable_account_numbers: bool
    tips_account: str

@dataclass
class Categories:
    track_classes: bool
    track_locations: bool

@dataclass
class Automation:
    pre_fill_forms: bool
    apply_credits_automatically: bool
    invoice_unbilled_activity: bool
    apply_bill_payments_automatically: bool

@dataclass
class Projects:
    organize_job_activity: bool

@dataclass
class Currency:
    home_currency: str
    multicurrency: bool

@dataclass
class OtherPreferences:
    date_format: str
    currency_format: str
    customer_label: str
    duplicate_check_warning: bool
    vendor_bill_warning: bool
    duplicate_journal_warning: bool
    sign_out_after_inactivity: str

@dataclass
class AdvancedSettings:
    accounting: Accounting
    company_type: CompanyType
    chart_of_accounts: ChartOfAccounts
    categories: Categories
    automation: Automation
    projects: Projects
    currency: Currency
    other_preferences: OtherPreferences

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedSettings':
        """Create an AdvancedSettings instance from a dictionary"""
        return cls(
            accounting=Accounting(**data['accounting']),
            company_type=CompanyType(**data['company_type']),
            chart_of_accounts=ChartOfAccounts(**data['chart_of_accounts']),
            categories=Categories(**data['categories']),
            automation=Automation(**data['automation']),
            projects=Projects(**data['projects']),
            currency=Currency(**data['currency']),
            other_preferences=OtherPreferences(**data['other_preferences'])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert AdvancedSettings instance to dictionary"""
        return {
            'accounting': {
                'fiscal_year_start': self.accounting.fiscal_year_start,
                'income_tax_year_start': self.accounting.income_tax_year_start,
                'accounting_method': self.accounting.accounting_method,
                'close_the_books': self.accounting.close_the_books
            },
            'company_type': {
                'tax_form': self.company_type.tax_form
            },
            'chart_of_accounts': {
                'enable_account_numbers': self.chart_of_accounts.enable_account_numbers,
                'tips_account': self.chart_of_accounts.tips_account
            },
            'categories': {
                'track_classes': self.categories.track_classes,
                'track_locations': self.categories.track_locations
            },
            'automation': {
                'pre_fill_forms': self.automation.pre_fill_forms,
                'apply_credits_automatically': self.automation.apply_credits_automatically,
                'invoice_unbilled_activity': self.automation.invoice_unbilled_activity,
                'apply_bill_payments_automatically': self.automation.apply_bill_payments_automatically
            },
            'projects': {
                'organize_job_activity': self.projects.organize_job_activity
            },
            'currency': {
                'home_currency': self.currency.home_currency,
                'multicurrency': self.currency.multicurrency
            },
            'other_preferences': {
                'date_format': self.other_preferences.date_format,
                'currency_format': self.other_preferences.currency_format,
                'customer_label': self.other_preferences.customer_label,
                'duplicate_check_warning': self.other_preferences.duplicate_check_warning,
                'vendor_bill_warning': self.other_preferences.vendor_bill_warning,
                'duplicate_journal_warning': self.other_preferences.duplicate_journal_warning,
                'sign_out_after_inactivity': self.other_preferences.sign_out_after_inactivity
            }
        }
