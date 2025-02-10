from datetime import datetime
import os
from typing import Dict, Optional, Any

from appwrite.query import Query
from appwrite.id import ID

from ..data_models.advanced_model import (
    FISCAL_YEAR_MONTHS,
    ACCOUNTING_METHODS,
    COMPANY_TAX_FORMS,
    DATE_FORMATS,
    CURRENCY_FORMATS,
    INACTIVITY_TIMEOUTS,
    DEFAULT_SETTINGS
)

class Advanced:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "advanced_settings"

    def __init__(
        self,
        user_id: str,
        # Required fields
        fiscal_year_start: str = DEFAULT_SETTINGS['fiscal_year_start'],
        income_tax_year_start: str = DEFAULT_SETTINGS['income_tax_year_start'],
        accounting_method: str = DEFAULT_SETTINGS['accounting_method'],
        tax_form: str = DEFAULT_SETTINGS['tax_form'],
        tips_account: str = DEFAULT_SETTINGS['tips_account'],
        # Optional fields with defaults
        close_the_books: bool = DEFAULT_SETTINGS['close_the_books'],
        enable_account_numbers: bool = DEFAULT_SETTINGS['enable_account_numbers'],
        track_classes: bool = DEFAULT_SETTINGS['track_classes'],
        track_locations: bool = DEFAULT_SETTINGS['track_locations'],
        pre_fill_forms: bool = DEFAULT_SETTINGS['pre_fill_forms'],
        apply_credits_automatically: bool = DEFAULT_SETTINGS['apply_credits_automatically'],
        invoice_unbilled_activity: bool = DEFAULT_SETTINGS['invoice_unbilled_activity'],
        apply_bill_payments_automatically: bool = DEFAULT_SETTINGS['apply_bill_payments_automatically'],
        organize_job_activity: bool = DEFAULT_SETTINGS['organize_job_activity'],
        home_currency: str = DEFAULT_SETTINGS['home_currency'],
        multicurrency: bool = DEFAULT_SETTINGS['multicurrency'],
        date_format: str = DEFAULT_SETTINGS['date_format'],
        currency_format: str = DEFAULT_SETTINGS['currency_format'],
        customer_label: str = DEFAULT_SETTINGS['customer_label'],
        duplicate_check_warning: bool = DEFAULT_SETTINGS['duplicate_check_warning'],
        vendor_bill_warning: bool = DEFAULT_SETTINGS['vendor_bill_warning'],
        duplicate_journal_warning: bool = DEFAULT_SETTINGS['duplicate_journal_warning'],
        sign_out_after_inactivity: str = DEFAULT_SETTINGS['sign_out_after_inactivity'],
        # System fields
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        document_id: Optional[str] = None
    ):
        self.user_id = user_id
        
        # Required fields
        self.fiscal_year_start = fiscal_year_start
        self.income_tax_year_start = income_tax_year_start
        self.accounting_method = accounting_method
        self.tax_form = tax_form
        self.tips_account = tips_account
        
        # Optional fields
        self.close_the_books = close_the_books
        self.enable_account_numbers = enable_account_numbers
        self.track_classes = track_classes
        self.track_locations = track_locations
        self.pre_fill_forms = pre_fill_forms
        self.apply_credits_automatically = apply_credits_automatically
        self.invoice_unbilled_activity = invoice_unbilled_activity
        self.apply_bill_payments_automatically = apply_bill_payments_automatically
        self.organize_job_activity = organize_job_activity
        self.home_currency = home_currency
        self.multicurrency = multicurrency
        self.date_format = date_format
        self.currency_format = currency_format
        self.customer_label = customer_label
        self.duplicate_check_warning = duplicate_check_warning
        self.vendor_bill_warning = vendor_bill_warning
        self.duplicate_journal_warning = duplicate_journal_warning
        self.sign_out_after_inactivity = sign_out_after_inactivity

        # System fields
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.document_id = document_id

    def _validate(self):
        """Validate advanced settings data"""
        if self.fiscal_year_start not in FISCAL_YEAR_MONTHS:
            raise ValueError(f"Invalid fiscal year start month. Must be one of: {FISCAL_YEAR_MONTHS}")

        if self.accounting_method not in ACCOUNTING_METHODS:
            raise ValueError(f"Invalid accounting method. Must be one of: {ACCOUNTING_METHODS}")

        if self.tax_form not in COMPANY_TAX_FORMS:
            raise ValueError(f"Invalid tax form. Must be one of: {COMPANY_TAX_FORMS}")

        if self.date_format not in DATE_FORMATS:
            raise ValueError(f"Invalid date format. Must be one of: {DATE_FORMATS}")

        if self.currency_format not in CURRENCY_FORMATS:
            raise ValueError(f"Invalid currency format. Must be one of: {CURRENCY_FORMATS}")

        if self.sign_out_after_inactivity not in INACTIVITY_TIMEOUTS:
            raise ValueError(f"Invalid inactivity timeout. Must be one of: {INACTIVITY_TIMEOUTS}")

    def to_dict(self, for_appwrite: bool = False) -> Dict[str, Any]:
        """Convert advanced settings to dictionary"""
        data = {
            'user_id': self.user_id,
            'fiscal_year_start': self.fiscal_year_start,
            'income_tax_year_start': self.income_tax_year_start,
            'accounting_method': self.accounting_method,
            'tax_form': self.tax_form,
            'tips_account': self.tips_account,
            'close_the_books': self.close_the_books,
            'enable_account_numbers': self.enable_account_numbers,
            'track_classes': self.track_classes,
            'track_locations': self.track_locations,
            'pre_fill_forms': self.pre_fill_forms,
            'apply_credits_automatically': self.apply_credits_automatically,
            'invoice_unbilled_activity': self.invoice_unbilled_activity,
            'apply_bill_payments_automatically': self.apply_bill_payments_automatically,
            'organize_job_activity': self.organize_job_activity,
            'home_currency': self.home_currency,
            'multicurrency': self.multicurrency,
            'date_format': self.date_format,
            'currency_format': self.currency_format,
            'customer_label': self.customer_label,
            'duplicate_check_warning': self.duplicate_check_warning,
            'vendor_bill_warning': self.vendor_bill_warning,
            'duplicate_journal_warning': self.duplicate_journal_warning,
            'sign_out_after_inactivity': self.sign_out_after_inactivity,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if not for_appwrite and self.document_id:
            data['document_id'] = self.document_id
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Advanced':
        """Create advanced settings from dictionary"""
        return cls(
            user_id=data['user_id'],
            fiscal_year_start=data['fiscal_year_start'],
            income_tax_year_start=data['income_tax_year_start'],
            accounting_method=data['accounting_method'],
            tax_form=data['tax_form'],
            tips_account=data['tips_account'],
            close_the_books=data.get('close_the_books', DEFAULT_SETTINGS['close_the_books']),
            enable_account_numbers=data.get('enable_account_numbers', DEFAULT_SETTINGS['enable_account_numbers']),
            track_classes=data.get('track_classes', DEFAULT_SETTINGS['track_classes']),
            track_locations=data.get('track_locations', DEFAULT_SETTINGS['track_locations']),
            pre_fill_forms=data.get('pre_fill_forms', DEFAULT_SETTINGS['pre_fill_forms']),
            apply_credits_automatically=data.get('apply_credits_automatically', DEFAULT_SETTINGS['apply_credits_automatically']),
            invoice_unbilled_activity=data.get('invoice_unbilled_activity', DEFAULT_SETTINGS['invoice_unbilled_activity']),
            apply_bill_payments_automatically=data.get('apply_bill_payments_automatically', DEFAULT_SETTINGS['apply_bill_payments_automatically']),
            organize_job_activity=data.get('organize_job_activity', DEFAULT_SETTINGS['organize_job_activity']),
            home_currency=data.get('home_currency', DEFAULT_SETTINGS['home_currency']),
            multicurrency=data.get('multicurrency', DEFAULT_SETTINGS['multicurrency']),
            date_format=data.get('date_format', DEFAULT_SETTINGS['date_format']),
            currency_format=data.get('currency_format', DEFAULT_SETTINGS['currency_format']),
            customer_label=data.get('customer_label', DEFAULT_SETTINGS['customer_label']),
            duplicate_check_warning=data.get('duplicate_check_warning', DEFAULT_SETTINGS['duplicate_check_warning']),
            vendor_bill_warning=data.get('vendor_bill_warning', DEFAULT_SETTINGS['vendor_bill_warning']),
            duplicate_journal_warning=data.get('duplicate_journal_warning', DEFAULT_SETTINGS['duplicate_journal_warning']),
            sign_out_after_inactivity=data.get('sign_out_after_inactivity', DEFAULT_SETTINGS['sign_out_after_inactivity']),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            document_id=data.get('$id')  # Appwrite uses $id for document ID
        )

    @classmethod
    def get_database(cls):
        """Get Appwrite database instance"""
        from config.appwrite_setup import databases
        return databases

    @classmethod
    def create_settings(cls, **kwargs) -> 'Advanced':
        """Create new advanced settings"""
        # Check if settings already exist for user
        existing = cls.get_settings(kwargs['user_id'])
        if existing:
            raise ValueError("Advanced settings already exist for this user")
            
        settings = cls(**kwargs)
        settings._validate()
        
        database = cls.get_database()
        data = settings.to_dict(for_appwrite=True)
        
        try:
            result = database.create_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=ID.unique(),
                data=data,
                permissions=['read("users")']
            )
            return cls.from_dict(result)
        except Exception as e:
            raise ValueError(f"Failed to create advanced settings: {str(e)}")

    @classmethod
    def get_settings(cls, user_id: str) -> Optional['Advanced']:
        """Get advanced settings by user_id"""
        database = cls.get_database()
        try:
            result = database.list_documents(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            if result['total'] == 0:
                return None
                
            return cls.from_dict(result['documents'][0])
        except Exception as e:
            raise ValueError(f"Failed to get advanced settings: {str(e)}")

    def update(self) -> 'Advanced':
        """Update advanced settings"""
        if not self.document_id:
            raise ValueError("Cannot update settings without document_id")
            
        self._validate()
        database = self.get_database()
        
        try:
            result = database.update_document(
                database_id=self.DATABASE_ID,
                collection_id=self.COLLECTION_ID,
                document_id=self.document_id,
                data=self.to_dict(for_appwrite=True)
            )
            return self.from_dict(result)
        except Exception as e:
            raise ValueError(f"Failed to update advanced settings: {str(e)}")

    @classmethod
    def delete_settings(cls, document_id: str):
        """Delete advanced settings"""
        database = cls.get_database()
        try:
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=document_id
            )
        except Exception as e:
            raise ValueError(f"Failed to delete advanced settings: {str(e)}")