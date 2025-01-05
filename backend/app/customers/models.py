from datetime import datetime
import json
import os
import random
from typing import Dict, List, Optional

class Address:
    def __init__(self, street: str, city: str, state: str, postal_code: str, country: str):
        self.street = street
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country = country

    def to_dict(self) -> Dict:
        return {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Address':
        return Address(
            street=data['street'],
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country=data['country']
        )

class Customer:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @staticmethod
    def get_user_data_file(uid: str) -> str:
        """Get the path to the user's customers.json file"""
        return os.path.join(Customer.BASE_DIR, 'data', uid, 'customers.json')

    @staticmethod
    def generate_customer_id() -> str:
        """Generate a random 8-digit ID with a dash in the middle"""
        while True:
            first_half = str(random.randint(1000, 9999))
            second_half = str(random.randint(1000, 9999))
            id = f"{first_half}-{second_half}"
            return id

    def __init__(self, id: str, customer_no: str, first_name: str, last_name: str, 
                 email: str, phone: str, billing_address: Address,
                 use_billing_for_shipping: bool = True, shipping_address: Optional[Address] = None,
                 company_name: Optional[str] = None, website: Optional[str] = None,
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.customer_no = customer_no
        self.first_name = first_name
        self.last_name = last_name
        self.company_name = company_name
        self.email = email
        self.phone = phone
        self.website = website
        self.billing_address = billing_address
        self.use_billing_for_shipping = use_billing_for_shipping
        self.shipping_address = shipping_address if not use_billing_for_shipping else None
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'customer_no': self.customer_no,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'billing_address': self.billing_address.to_dict(),
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'use_billing_for_shipping': self.use_billing_for_shipping,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Customer':
        return Customer(
            id=data['id'],
            customer_no=data['customer_no'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            company_name=data.get('company_name'),
            email=data['email'],
            phone=data['phone'],
            website=data.get('website'),
            billing_address=Address.from_dict(data['billing_address']),
            shipping_address=Address.from_dict(data['shipping_address']) if data.get('shipping_address') else None,
            use_billing_for_shipping=data.get('use_billing_for_shipping', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

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
    def get_by_id(uid: str, id: str) -> Optional['Customer']:
        """Get customer by ID"""
        customers = Customer.get_all(uid)
        return next((customer for customer in customers if customer.id == id), None)

    @staticmethod
    def is_id_unique(id: str, customers: List['Customer']) -> bool:
        """Check if an ID is unique among existing customers"""
        return not any(customer.id == id for customer in customers)

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
            customer_numbers = [c.customer_no for c in customers]
            
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
            data['customers'] = [c for c in data['customers'] if c['id'] != self.id]
            
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
                data['customers'] = [c for c in data['customers'] if c['id'] != self.id]
                data['metadata']['lastUpdated'] = datetime.utcnow().isoformat()

                # Save updated data
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            raise Exception(f"Error deleting customer: {str(e)}")
