from datetime import datetime
import json
import os
import random
from typing import Dict, List, Optional

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID

class Customer:
    DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
    COLLECTION_ID = "customers"

    def __init__(self, customer_id: str, user_id: str, first_name: str, last_name: str, 
                 customer_email: str, phone: str,
                 # Billing address fields
                 billing_street: str, billing_city: str, billing_state: str,
                 billing_postal_code: str, billing_country: str,
                 # Optional fields
                 company_name: Optional[str] = None,
                 website: Optional[str] = None,
                 use_billing_for_shipping: bool = True,
                 # Optional shipping address fields
                 shipping_street: Optional[str] = None,
                 shipping_city: Optional[str] = None,
                 shipping_state: Optional[str] = None,
                 shipping_postal_code: Optional[str] = None,
                 shipping_country: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None):
        
        self.customer_id = customer_id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.customer_email = customer_email
        self.phone = phone
        self.company_name = company_name
        self.website = website
        
        # Billing address
        self.billing_street = billing_street
        self.billing_city = billing_city
        self.billing_state = billing_state
        self.billing_postal_code = billing_postal_code
        self.billing_country = billing_country
        
        # Shipping address
        self.use_billing_for_shipping = use_billing_for_shipping
        if use_billing_for_shipping:
            self.shipping_street = billing_street
            self.shipping_city = billing_city
            self.shipping_state = billing_state
            self.shipping_postal_code = billing_postal_code
            self.shipping_country = billing_country
        else:
            self.shipping_street = shipping_street
            self.shipping_city = shipping_city
            self.shipping_state = shipping_state
            self.shipping_postal_code = shipping_postal_code
            self.shipping_country = shipping_country
        
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'customer_email': self.customer_email,
            'phone': self.phone,
            'company_name': self.company_name,
            'website': self.website,
            'billing_street': self.billing_street,
            'billing_city': self.billing_city,
            'billing_state': self.billing_state,
            'billing_postal_code': self.billing_postal_code,
            'billing_country': self.billing_country,
            'use_billing_for_shipping': self.use_billing_for_shipping,
            'shipping_street': self.shipping_street,
            'shipping_city': self.shipping_city,
            'shipping_state': self.shipping_state,
            'shipping_postal_code': self.shipping_postal_code,
            'shipping_country': self.shipping_country,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Customer':
        return Customer(
            customer_id=data['customer_id'],
            user_id=data['user_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            customer_email=data['customer_email'],
            phone=data['phone'],
            company_name=data.get('company_name'),
            website=data.get('website'),
            billing_street=data['billing_street'],
            billing_city=data['billing_city'],
            billing_state=data['billing_state'],
            billing_postal_code=data['billing_postal_code'],
            billing_country=data['billing_country'],
            use_billing_for_shipping=data.get('use_billing_for_shipping', True),
            shipping_street=data.get('shipping_street'),
            shipping_city=data.get('shipping_city'),
            shipping_state=data.get('shipping_state'),
            shipping_postal_code=data.get('shipping_postal_code'),
            shipping_country=data.get('shipping_country'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    @staticmethod
    def generate_customer_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(100000, 999999))
            second_half = str(random.randint(100000, 999999))
            id = f"CUST{first_half}-{second_half}"
            return id

    @classmethod
    def get_database(cls):
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        return Databases(client)

    @classmethod
    def create_customer(cls, user_id: str, first_name: str, last_name: str,
                       customer_email: str, phone: str,
                       billing_street: str, billing_city: str,
                       billing_state: str, billing_postal_code: str,
                       billing_country: str, company_name: Optional[str] = None,
                       website: Optional[str] = None,
                       use_billing_for_shipping: bool = True,
                       shipping_street: Optional[str] = None,
                       shipping_city: Optional[str] = None,
                       shipping_state: Optional[str] = None,
                       shipping_postal_code: Optional[str] = None,
                       shipping_country: Optional[str] = None) -> 'Customer':
        """Create a new customer in Appwrite"""
        try:
            print("\nAttempting to create customer:")
            print(f"customer_email: {customer_email}")
            print(f"phone: {phone}")
            
            # Check for existing customer
            existing = cls.check_existing_customer(user_id, customer_email, phone)
            print(f"Existing customer check result: {existing}")
            
            if existing:
                print("Found existing customer, raising exception")
                raise Exception(f"Customer already exists with customer_email {customer_email} or phone {phone}")

            print("No existing customer found, proceeding with creation")
            client = Client()
            client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
            client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
            client.set_key(os.getenv('APPWRITE_API_KEY'))
            
            database = Databases(client)
            customer_id = cls.generate_customer_id()
            
            # If use_billing_for_shipping is true, set shipping address to billing address
            if use_billing_for_shipping:
                shipping_street = billing_street
                shipping_city = billing_city
                shipping_state = billing_state
                shipping_postal_code = billing_postal_code
                shipping_country = billing_country

            # Create customer data
            data = {
                'customer_id': customer_id,
                'user_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'customer_email': customer_email,
                'phone': phone,
                'company_name': company_name,
                'website': website,
                # Billing address
                'billing_street': billing_street,
                'billing_city': billing_city,
                'billing_state': billing_state,
                'billing_postal_code': billing_postal_code,
                'billing_country': billing_country,
                # Shipping address
                'use_billing_for_shipping': use_billing_for_shipping,
                'shipping_street': shipping_street,
                'shipping_city': shipping_city,
                'shipping_state': shipping_state,
                'shipping_postal_code': shipping_postal_code,
                'shipping_country': shipping_country,
                # Timestamps
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = database.create_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=customer_id,
                data=data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error creating customer: {str(e)}")
            raise

    @classmethod
    def check_existing_customer(cls, user_id: str, customer_email: str, phone: str) -> Optional['Customer']:
        """Check if a customer already exists with the given customer_email or phone"""
        try:
            print(f"\nChecking for existing customer:")
            print(f"user_id: {user_id}")
            print(f"customer_email: {customer_email}")
            print(f"phone: {phone}")
            
            database = cls.get_database()
            
            customer_email_result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.equal('customer_email', customer_email)
                ]
            )
            
            print(f"customer_email query result: {customer_email_result}")
            
            if customer_email_result['documents']:
                print("Found existing customer by customer_email")
                return cls.from_dict(customer_email_result['documents'][0])
            
            phone_result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[
                    Query.equal('user_id', user_id),
                    Query.equal('phone', phone)
                ]
            )
            
            print(f"Phone query result: {phone_result}")
            
            if phone_result['documents']:
                print("Found existing customer by phone")
                return cls.from_dict(phone_result['documents'][0])
            
            print("No existing customer found")
            return None
            
        except Exception as e:
            print(f"Error checking existing customer: {str(e)}")
            print(f"Exception type: {type(e)}")
            print(f"Exception args: {e.args}")
            return None

    @classmethod
    def get_customers_by_user(cls, user_id: str) -> List['Customer']:
        """Get all customers for a specific user"""
        try:
            database = cls.get_database()
            result = database.list_documents(
                cls.DATABASE_ID,
                cls.COLLECTION_ID,
                queries=[Query.equal('user_id', user_id)]
            )
            
            customers = []
            for doc in result['documents']:
                customer = cls.from_dict(doc)
                customers.append(customer)
                
            return customers
            
        except Exception as e:
            raise Exception(f"Error getting customers: {str(e)}")

    @classmethod
    def get_customer(cls, customer_id: str, user_id: str = None) -> Optional['Customer']:
        """Get a customer by ID. If user_id is provided, verify ownership."""
        try:
            client = Client()
            client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
            client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
            client.set_key(os.getenv('APPWRITE_API_KEY'))
            
            database = Databases(client)
            result = database.get_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=customer_id
            )
            
            customer = cls.from_dict(result)
            
            # If user_id is provided, verify ownership
            if user_id and customer.user_id != user_id:
                return None
                
            return customer
            
        except Exception as e:
            print(f"Error getting customer: {str(e)}")
            return None

    @classmethod
    def update_customer(cls, customer_id: str, user_id: str, data: Dict) -> Optional['Customer']:
        """Update a customer, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_customer(customer_id, user_id)
            if not existing:
                return None
                
            client = Client()
            client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
            client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
            client.set_key(os.getenv('APPWRITE_API_KEY'))
            
            database = Databases(client)
            
            # Ensure we don't modify user_id
            data['user_id'] = user_id
            data['updated_at'] = datetime.utcnow().isoformat()
            
            result = database.update_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=customer_id,
                data=data
            )
            
            return cls.from_dict(result)
            
        except Exception as e:
            print(f"Error updating customer: {str(e)}")
            return None

    @classmethod
    def delete_customer(cls, customer_id: str, user_id: str) -> bool:
        """Delete a customer, verifying ownership first"""
        try:
            # First verify ownership
            existing = cls.get_customer(customer_id, user_id)
            if not existing:
                return False
                
            client = Client()
            client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
            client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
            client.set_key(os.getenv('APPWRITE_API_KEY'))
            
            database = Databases(client)
            database.delete_document(
                database_id=cls.DATABASE_ID,
                collection_id=cls.COLLECTION_ID,
                document_id=customer_id
            )
            
            return True
            
        except Exception as e:
            print(f"Error deleting customer: {str(e)}")
            return False

    @staticmethod
    def get_user_data_file(uid: str) -> str:
        """Get the path to the user's customers.json file"""
        return os.path.join('data', uid, 'customers.json')

    @staticmethod
    def get_all(uid: str) -> List['Customer']:
        """Get all customers"""
        try:
            file_path = Customer.get_user_data_file(uid)
            if not os.path.exists(file_path):
                return []
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [Customer.from_dict(customer_data) for customer_data in data.get('customers', [])]
        except Exception as e:
            print(f"Error loading customers: {str(e)}")
            return []

    @staticmethod
    def get_by_id(uid: str, customer_id: str) -> Optional['Customer']:
        """Get customer by ID"""
        customers = Customer.get_all(uid)
        return next((customer for customer in customers if customer.customer_id == customer_id), None)

    @staticmethod
    def is_id_unique(customer_id: str, customers: List['Customer']) -> bool:
        """Check if an ID is unique among existing customers"""
        return not any(customer.customer_id == customer_id for customer in customers)

    @staticmethod
    def exists(uid: str, first_name: str, last_name: str) -> bool:
        """Check if a customer with the given first and last name exists"""
        customers = Customer.get_all(uid)
        return any(
            c.first_name.lower() == first_name.lower() and 
            c.last_name.lower() == last_name.lower() 
            for c in customers
        )

    @staticmethod
    def get_next_number(uid: str) -> str:
        """Get next customer number"""
        try:
            customers = Customer.get_all(uid)
            if not customers:
                current_year = datetime.now().year
                return f"CUST-{current_year}-001"

            # Extract all customer numbers
            customer_numbers = [c.customer_id for c in customers]
            
            # Get the highest number
            current_year = datetime.now().year
            current_year_prefix = f"CUST-{current_year}-"
            current_year_numbers = [int(n.split('-')[2]) for n in customer_numbers if n.startswith(current_year_prefix)]
            
            if current_year_numbers:
                next_number = max(current_year_numbers) + 1
            else:
                next_number = 1
                
            return f"{current_year_prefix}{next_number:03d}"
        except Exception as e:
            print(f"Error generating next customer number: {str(e)}")
            current_year = datetime.now().year
            return f"CUST-{current_year}-001"

    def save(self, uid: str) -> None:
        """Save the customer to the user's customers.json file"""
        file_path = Customer.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                data = {"customers": [], "metadata": {"lastUpdated": datetime.utcnow().isoformat()}}

            # Remove existing customer if it exists
            data['customers'] = [c for c in data['customers'] if c['customer_id'] != self.customer_id]
            
            # Add updated customer
            data['customers'].append(self.to_dict())
            data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error saving customer: {str(e)}")

    def delete(self, uid: str) -> None:
        """Delete the customer from the user's customers.json file"""
        file_path = Customer.get_user_data_file(uid)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Remove customer
                data['customers'] = [c for c in data['customers'] if c['customer_id'] != self.customer_id]
                data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

                # Save updated data
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error deleting customer: {str(e)}")
