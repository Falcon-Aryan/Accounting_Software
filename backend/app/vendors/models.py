from datetime import datetime
import json
import os
import random
from typing import Dict, List, Optional

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID

class Vendor:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "vendors"

    def __init__(self, vendor_id: str, user_id: str, company_name: str, contact_name: str, 
                 vendor_email: str, phone: str,
                 # Billing address fields
                 billing_street: str, billing_city: str, billing_state: str,
                 billing_postal_code: str, billing_country: str,
                 # Optional fields
                 website: Optional[str] = None,
                 payment_terms: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None):
        
        self.vendor_id = vendor_id
        self.user_id = user_id
        self.company_name = company_name
        self.contact_name = contact_name
        self.vendor_email = vendor_email
        self.phone = phone
        self.website = website
        self.payment_terms = payment_terms
        
        # Billing address
        self.billing_street = billing_street
        self.billing_city = billing_city
        self.billing_state = billing_state
        self.billing_postal_code = billing_postal_code
        self.billing_country = billing_country
        
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            'vendor_id': self.vendor_id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'vendor_email': self.vendor_email,
            'phone': self.phone,
            'website': self.website,
            'payment_terms': self.payment_terms,
            'billing_street': self.billing_street,
            'billing_city': self.billing_city,
            'billing_state': self.billing_state,
            'billing_postal_code': self.billing_postal_code,
            'billing_country': self.billing_country,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Vendor':
        return Vendor(
            vendor_id=data['vendor_id'],
            user_id=data['user_id'],
            company_name=data['company_name'],
            contact_name=data['contact_name'],
            vendor_email=data['vendor_email'],
            phone=data['phone'],
            website=data.get('website'),
            payment_terms=data.get('payment_terms'),
            billing_street=data['billing_street'],
            billing_city=data['billing_city'],
            billing_state=data['billing_state'],
            billing_postal_code=data['billing_postal_code'],
            billing_country=data['billing_country'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    @staticmethod
    def generate_vendor_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"VEND{first_half}-{second_half}"
            return id

    @classmethod
    def get_database(cls):
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)

    @classmethod
    def create_vendor(cls, user_id: str, company_name: str, contact_name: str,
                     vendor_email: str, phone: str,
                     billing_street: str, billing_city: str,
                     billing_state: str, billing_postal_code: str,
                     billing_country: str, website: Optional[str] = None,
                     payment_terms: Optional[str] = None) -> 'Vendor':
        """Create a new vendor in Appwrite"""
        try:
            print("\nAttempting to create vendor:")
            print(f"vendor_email: {vendor_email}")
            print(f"phone: {phone}")
            
            # Check for existing vendor
            existing = cls.check_existing_vendor(user_id, vendor_email, phone)
            print(f"Existing vendor check result: {existing}")
            
            if existing:
                print("Found existing vendor, raising exception")
                raise Exception(f"Vendor already exists with vendor_email {vendor_email} or phone {phone}")

            print("No existing vendor found, proceeding with creation")
            database = cls.get_database()
            vendor_id = cls.generate_vendor_id()
            
            # Create vendor data
            data = {
                'vendor_id': vendor_id,
                'user_id': user_id,
                'company_name': company_name,
                'contact_name': contact_name,
                'vendor_email': vendor_email,
                'phone': phone,
                'website': website,
                'payment_terms': payment_terms,
                'billing_street': billing_street,
                'billing_city': billing_city,
                'billing_state': billing_state,
                'billing_postal_code': billing_postal_code,
                'billing_country': billing_country,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = database.create_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=vendor_id,
                data=data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error creating vendor: {str(e)}")
            raise

    @classmethod
    def check_existing_vendor(cls, user_id: str, vendor_email: str, phone: str) -> Optional['Vendor']:
        """Check if a vendor already exists with the given vendor_email or phone"""
        try:
            print(f"\nChecking for existing vendor:")
            print(f"user_id: {user_id}")
            print(f"vendor_email: {vendor_email}")
            print(f"phone: {phone}")
            
            database = cls.get_database()
            
            vendor_email_result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.equal('vendor_email', vendor_email)
                ]
            )
            
            if vendor_email_result['documents']:
                print("Found existing vendor by vendor_email")
                return cls.from_dict(vendor_email_result['documents'][0])
            
            phone_result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.equal('phone', phone)
                ]
            )
            
            if phone_result['documents']:
                print("Found existing vendor by phone")
                return cls.from_dict(phone_result['documents'][0])
            
            print("No existing vendor found")
            return None
            
        except Exception as e:
            print(f"Error checking existing vendor: {str(e)}")
            return None

    @classmethod
    def get_vendors_by_user(cls, user_id: str) -> List['Vendor']:
        """Get all vendors for a specific user"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            vendors = []
            for doc in result['documents']:
                vendor = cls.from_dict(doc)
                vendors.append(vendor)
                
            return vendors
            
        except Exception as e:
            raise Exception(f"Error getting vendors: {str(e)}")

    @classmethod
    def get_vendor(cls, vendor_id: str, user_id: str = None) -> Optional['Vendor']:
        """Get a vendor by ID. If user_id is provided, verify ownership."""
        try:
            database = cls.get_database()
            result = database.get_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=vendor_id
            )
            
            vendor = cls.from_dict(result)
            
            # If user_id is provided, verify ownership
            if user_id and vendor.user_id != user_id:
                return None
                
            return vendor
            
        except Exception as e:
            print(f"Error getting vendor: {str(e)}")
            return None

    @classmethod
    def update_vendor(cls, vendor_id: str, user_id: str, data: Dict) -> Optional['Vendor']:
        """Update a vendor, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_vendor(vendor_id, user_id)
            if not existing:
                return None
                
            database = cls.get_database()
            
            # Ensure we don't modify user_id
            data['user_id'] = user_id
            data['updated_at'] = datetime.utcnow().isoformat()
            
            result = database.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=vendor_id,
                data=data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error updating vendor: {str(e)}")
            return None

    @classmethod
    def delete_vendor(cls, vendor_id: str, user_id: str) -> bool:
        """Delete a vendor, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_vendor(vendor_id, user_id)
            if not existing:
                return False
                
            database = cls.get_database()
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=vendor_id
            )
            
            return True
            
        except Exception as e:
            print(f"Error deleting vendor: {str(e)}")
            return False