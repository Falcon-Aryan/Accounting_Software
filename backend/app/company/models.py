from datetime import datetime
import os
from typing import Dict, Optional, Any

from appwrite.query import Query
from appwrite.id import ID

from ..data_models.company_model import (
    COMPANY_TAX_FORMS,
    INDUSTRY_TYPES,
    IDENTITY_TYPES,
    COMPANY_STATUS
)

class Company:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "company_settings"

    def __init__(
        self,
        user_id: str,
        company_name: str,
        legal_name: str,
        identity_type: str,
        identity_number: str,
        tax_form: str,
        industry: str,
        company_email: str,
        customer_facing_email: str,
        company_phone: str,
        # Company address fields
        company_street: str,
        company_city: str,
        company_state: str,
        company_postal_code: str,
        company_country: str,
        # Optional fields
        same_as_company_name: bool = True,
        same_as_company_email: bool = True,
        website: Optional[str] = None,
        # Optional legal address fields
        legal_street: Optional[str] = None,
        legal_city: Optional[str] = None,
        legal_state: Optional[str] = None,
        legal_postal_code: Optional[str] = None,
        legal_country: Optional[str] = None,
        same_as_company_address: bool = True,
        status: str = 'active',
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.user_id = user_id
        self.company_name = company_name
        self.legal_name = legal_name
        self.same_as_company_name = same_as_company_name
        self.identity_type = identity_type
        self.identity_number = identity_number
        self.tax_form = tax_form
        self.industry = industry
        self.company_email = company_email
        self.customer_facing_email = customer_facing_email
        self.same_as_company_email = same_as_company_email
        self.company_phone = company_phone
        self.website = website

        # Company address
        self.company_street = company_street
        self.company_city = company_city
        self.company_state = company_state
        self.company_postal_code = company_postal_code
        self.company_country = company_country

        # Legal address
        self.same_as_company_address = same_as_company_address
        self.legal_street = legal_street
        self.legal_city = legal_city
        self.legal_state = legal_state
        self.legal_postal_code = legal_postal_code
        self.legal_country = legal_country

        self.status = status
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validate company data"""
        if self.identity_type not in IDENTITY_TYPES:
            raise ValueError(f"Invalid identity type. Must be one of: {IDENTITY_TYPES}")

        if self.tax_form not in COMPANY_TAX_FORMS:
            raise ValueError(f"Invalid tax form. Must be one of: {COMPANY_TAX_FORMS}")

        if self.industry not in INDUSTRY_TYPES:
            raise ValueError(f"Invalid industry type. Must be one of: {INDUSTRY_TYPES}")

        if self.status not in COMPANY_STATUS:
            raise ValueError(f"Invalid status. Must be one of: {COMPANY_STATUS}")

    def to_dict(self, for_appwrite: bool = False) -> Dict[str, Any]:
        """Convert company to dictionary"""
        return {
            'user_id': self.user_id,
            'company_name': self.company_name,
            'legal_name': self.legal_name,
            'same_as_company_name': self.same_as_company_name,
            'identity_type': self.identity_type,
            'identity_number': self.identity_number,
            'tax_form': self.tax_form,
            'industry': self.industry,
            'company_email': self.company_email,
            'customer_facing_email': self.customer_facing_email,
            'same_as_company_email': self.same_as_company_email,
            'company_phone': self.company_phone,
            'website': self.website,
            'company_street': self.company_street,
            'company_city': self.company_city,
            'company_state': self.company_state,
            'company_postal_code': self.company_postal_code,
            'company_country': self.company_country,
            'legal_street': self.legal_street,
            'legal_city': self.legal_city,
            'legal_state': self.legal_state,
            'legal_postal_code': self.legal_postal_code,
            'legal_country': self.legal_country,
            'same_as_company_address': self.same_as_company_address,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Company':
        """Create company from dictionary"""
        return cls(
            user_id=data['user_id'],
            company_name=data['company_name'],
            legal_name=data['legal_name'],
            same_as_company_name=data.get('same_as_company_name', True),
            identity_type=data['identity_type'],
            identity_number=data['identity_number'],
            tax_form=data['tax_form'],
            industry=data['industry'],
            company_email=data['company_email'],
            customer_facing_email=data['customer_facing_email'],
            same_as_company_email=data.get('same_as_company_email', True),
            company_phone=data.get('company_phone'),
            website=data.get('website'),
            company_street=data['company_street'],
            company_city=data['company_city'],
            company_state=data['company_state'],
            company_postal_code=data['company_postal_code'],
            company_country=data['company_country'],
            legal_street=data.get('legal_street'),
            legal_city=data.get('legal_city'),
            legal_state=data.get('legal_state'),
            legal_postal_code=data.get('legal_postal_code'),
            legal_country=data.get('legal_country'),
            same_as_company_address=data.get('same_as_company_address', True),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    @classmethod
    def get_database(cls):
        """Get Appwrite database instance"""
        from config.appwrite_setup import databases
        return databases

    @classmethod
    def create_company(cls, **kwargs) -> 'Company':
        """Create a new company"""
        company = cls(**kwargs)
        company._validate()
        
        database = cls.get_database()
        data = company.to_dict(for_appwrite=True)
        
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
            raise ValueError(f"Failed to create company: {str(e)}")

    @classmethod
    def get_company(cls, user_id: str) -> Optional['Company']:
        """Get company by user_id"""
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
            raise ValueError(f"Failed to get company: {str(e)}")

    def update(self) -> 'Company':
        """Update company"""
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
            raise ValueError(f"Failed to update company: {str(e)}")

    @classmethod
    def delete_company(cls, document_id: str):
        """Delete company"""
        database = cls.get_database()
        try:
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=document_id
            )
        except Exception as e:
            raise ValueError(f"Failed to delete company: {str(e)}")