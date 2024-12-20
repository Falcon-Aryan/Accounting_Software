from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class CompanyNameInfo:
    company_name: str
    legal_name: str
    same_as_company_name: bool
    identity: str  # SSN or EIN
    tax_id: str

@dataclass
class CompanyType:
    tax_form: str
    industry: str

@dataclass
class ContactInfo:
    company_email: str
    customer_facing_email: str
    same_as_company_email: bool
    company_phone: str
    website: str

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert Address instance to dictionary"""
        return {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Create an Address instance from a dictionary"""
        return cls(
            street=data.get('street', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            zip_code=data.get('zip_code', ''),
            country=data.get('country', '')
        )

@dataclass
class CompanyAddress:
    company_address: Address
    legal_address: Optional[Address] = None
    same_as_company_address: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert CompanyAddress instance to dictionary"""
        result = {
            'company_address': self.company_address.to_dict(),
            'same_as_company_address': self.same_as_company_address
        }
        if self.legal_address:
            result['legal_address'] = self.legal_address.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyAddress':
        """Create a CompanyAddress instance from a dictionary"""
        company_address = Address.from_dict(data.get('company_address', {}))
        legal_address = None
        if data.get('legal_address'):
            legal_address = Address.from_dict(data.get('legal_address', {}))
        
        return cls(
            company_address=company_address,
            legal_address=legal_address,
            same_as_company_address=data.get('same_as_company_address', False)
        )

class Company:
    def __init__(self):
        self.company_name_info = CompanyNameInfo(
            company_name='',
            legal_name='',
            same_as_company_name=False,
            identity='',
            tax_id=''
        )
        self.company_type = CompanyType(
            tax_form='',
            industry=''
        )
        self.contact_info = ContactInfo(
            company_email='',
            customer_facing_email='',
            same_as_company_email=True,
            company_phone='',
            website=''
        )
        self.Address = CompanyAddress(
            company_address=Address(
                street='',
                city='',
                state='',
                zip_code='',
                country=''
            ),
            legal_address=Address(
                street='',
                city='',
                state='',
                zip_code='',
                country=''
            ),
            same_as_company_address=True
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Company instance to dictionary"""
        return {
            'company_name_info': {
                'company_name': self.company_name_info.company_name,
                'legal_name': self.company_name_info.legal_name,
                'same_as_company_name': self.company_name_info.same_as_company_name,
                'identity': self.company_name_info.identity,
                'tax_id': self.company_name_info.tax_id
            },
            'company_type': {
                'tax_form': self.company_type.tax_form,
                'industry': self.company_type.industry
            },
            'contact_info': {
                'company_email': self.contact_info.company_email,
                'customer_facing_email': self.contact_info.customer_facing_email,
                'same_as_company_email': self.contact_info.same_as_company_email,
                'company_phone': self.contact_info.company_phone,
                'website': self.contact_info.website
            },
            'Address': self.Address.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Company':
        """Create a Company instance from a dictionary"""
        company = cls()
        
        company_name_info_data = data.get('company_name_info', {})
        company.company_name_info = CompanyNameInfo(
            company_name=company_name_info_data.get('company_name', ''),
            legal_name=company_name_info_data.get('legal_name', ''),
            same_as_company_name=company_name_info_data.get('same_as_company_name', False),
            identity=company_name_info_data.get('identity', ''),
            tax_id=company_name_info_data.get('tax_id', '')
        )
        
        company_type_data = data.get('company_type', {})
        company.company_type = CompanyType(
            tax_form=company_type_data.get('tax_form', ''),
            industry=company_type_data.get('industry', '')
        )
        
        contact_info_data = data.get('contact_info', {})
        company.contact_info = ContactInfo(
            company_email=contact_info_data.get('company_email', ''),
            customer_facing_email=contact_info_data.get('customer_facing_email', ''),
            same_as_company_email=contact_info_data.get('same_as_company_email', True),
            company_phone=contact_info_data.get('company_phone', ''),
            website=contact_info_data.get('website', '')
        )
        
        company.Address = CompanyAddress.from_dict(data.get('Address', {}))
        
        return company
