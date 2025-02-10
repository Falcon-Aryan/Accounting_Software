from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.input_file import InputFile
from appwrite.id import ID
import os
import sys
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_models.transaction_types import TRANSACTION_TYPES, TRANSACTION_STATUSES
from app.data_models.customer_types import CUSTOMER_STATES
from app.data_models.estimates_types import ESTIMATE_STATUSES, ESTIMATE_PAYMENT_TERMS
from app.data_models.invoices_types import INVOICE_STATUSES, INVOICE_PAYMENT_TERMS
from app.data_models.purchase_order_types import PO_STATUSES, PO_PAYMENT_TERMS
from app.data_models.vendors_types import VENDOR_STATES
from app.data_models.company_model import COMPANY_TAX_FORMS, INDUSTRY_TYPES, ADDRESS_TYPES, IDENTITY_TYPES, COMPANY_STATUS, COMPANY_SIZE

# Load environment variables
load_dotenv()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize Database service
databases = Databases(client)

# Initialize Users service
users_service = Users(client)

# Use existing database ID
DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')

def verify_attribute_exists(database_id, collection_id, attribute_name, max_retries=3, delay=5):
    """Verify if an attribute exists in a collection"""
    for attempt in range(max_retries):
        try:
            attributes = databases.list_attributes(database_id, collection_id)
            for attr in attributes['attributes']:
                if attr['key'] == attribute_name:
                    return True
            if attempt < max_retries - 1:
                print(f"Attribute {attribute_name} not found, retrying in {delay} seconds...")
                time.sleep(delay)
        except Exception as e:
            print(
                f"Attempt {attempt + 1}: Error verifying attribute {attribute_name}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return False


def verify_index_exists(database_id, collection_id, index_name, max_retries=3, delay=5):
    """Verify if an index exists in a collection"""
    for attempt in range(max_retries):
        try:
            indexes = databases.list_indexes(database_id, collection_id)
            for idx in indexes['indexes']:
                if idx['key'] == index_name:
                    return True
            if attempt < max_retries - 1:
                print(f"Index {index_name} not found, retrying in {delay} seconds...")
                time.sleep(delay)
        except Exception as e:
            print(
                f"Attempt {attempt + 1}: Error verifying index {index_name}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return False


def create_attribute_with_retry(database_id, collection_id, attribute_type, key, max_retries=3, delay=5, **kwargs):
    """Create an attribute with retry logic"""
    for attempt in range(max_retries):
        try:
            if attribute_type == 'string':
                databases.create_string_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    **kwargs
                )
            elif attribute_type == 'integer':
                databases.create_integer_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    **kwargs
                )
            elif attribute_type == 'float':
                databases.create_float_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    **kwargs
                )
            elif attribute_type == 'boolean':
                databases.create_boolean_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    **kwargs
                )
            elif attribute_type == 'datetime':
                databases.create_datetime_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    **kwargs
                )
            elif attribute_type == 'enum':
                databases.create_enum_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    **kwargs
                )

            # Verify attribute was created
            if verify_attribute_exists(database_id, collection_id, key):
                print(f"Successfully created attribute: {key}")
                return True

        except Exception as e:
            print(
                f"Attempt {attempt + 1}: Error creating attribute {key}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    return False


def create_index_with_retry(database_id, collection_id, key, type, attributes, orders=None, max_retries=3, delay=5):
    """Create an index with retry logic"""
    # First verify all attributes exist
    for attr in attributes:
        if not verify_attribute_exists(database_id, collection_id, attr):
            print(f"Cannot create index {key}: attribute {attr} does not exist")
            return False

    for attempt in range(max_retries):
        try:
            if orders:
                databases.create_index(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    type=type,
                    attributes=attributes,
                    orders=orders
                )
            else:
                databases.create_index(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=key,
                    type=type,
                    attributes=attributes
                )

            # Verify index was created
            if verify_index_exists(database_id, collection_id, key):
                print(f"Successfully created index: {key}")
                return True

        except Exception as e:
            print(
                f"Attempt {attempt + 1}: Error creating index {key}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    return False


def sync_users_with_database():
    try:
        # Get all users from Auth
        auth_users = users_service.list()

        # For each user in Auth
        for user in auth_users['users']:
            try:
                # Create or update user document in database
                databases.create_document(
                    database_id=DATABASE_ID,
                    collection_id='users',
                    document_id=user['$id'],
                    data={
                        'user_id': user['$id'],
                        'email': user['email'],
                        'name': user.get('name', ''),
                        'created_at': user['$createdAt']
                    }
                )
            except Exception as e:
                if 'Document already exists' not in str(e):
                    print(f"Error syncing user {user['$id']}: {str(e)}")
                    continue
        print("Successfully synced users from Auth to database")
    except Exception as e:
        print(f"Error syncing users: {str(e)}")


def setup_appwrite():
    try:
        print(f"Using existing database with ID: {DATABASE_ID}")

        # Create users collection
        try:
            users = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='users',
                name='Users',
                permissions=['read("any")', 'write("any")']
            )
            print("Created users collection")

            # User attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='users',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='users',
                attribute_type='string',
                key='email',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='users',
                attribute_type='string',
                key='name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='users',
                attribute_type='string',
                key='company_name',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='users',
                attribute_type='string',
                key='phone',
                size=50,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='users',
                attribute_type='string',
                key='created_at',
                size=255,
                required=False
            )

            print("Created user attributes")

        except Exception as e:
            print(f"Error creating users collection: {str(e)}")

        time.sleep(5)

        # Create customers collection
        try:
            customers = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='customers',
                name='Customers',
                permissions=['read("any")', 'write("any")']
            )
            print("Created customers collection")

            # Add user_id to customers
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            # Customer basic info
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='customer_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='first_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='last_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='customer_email',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='phone',
                size=50,
                required=True
            )

            time.sleep(5)

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='company_name',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='website',
                size=255,
                required=False
            )

            # Billing Address
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='billing_street',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='billing_city',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='enum',
                key='billing_state',
                elements=CUSTOMER_STATES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='billing_postal_code',
                size=20,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='billing_country',
                size=100,
                required=True
            )

            # Shipping Address
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='shipping_street',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='shipping_city',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='enum',
                key='shipping_state',
                elements=CUSTOMER_STATES,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='shipping_postal_code',
                size=20,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='shipping_country',
                size=100,
                required=False
            )

            # Shipping Address (optional)
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='boolean',
                key='use_billing_for_shipping',
                default=True,
                required=False
            )

            # Timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='created_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                attribute_type='string',
                key='updated_at',
                size=30,
                required=False
            )

            # Indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                key='customer_email_index',
                type='key',
                attributes=['customer_email'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                key='customer_id_index',
                type='key',
                attributes=['customer_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                key='user_id_idx',
                type='key',
                attributes=['user_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='customers',
                key='phone_index',
                type='key',
                attributes=['phone'],
                orders=['ASC']
            )

            print("Created all customer attributes and indexes")

        except Exception as e:
            print(f"Collection might already exist: {str(e)}")

        time.sleep(5)

        # Create vendors collection
        try:
            vendors = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='vendors',
                name='Vendors',
                permissions=['read("any")', 'write("any")']
            )
            print("Created vendors collection")

            # Add user_id to vendors
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            # Vendor basic info
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='vendor_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='company_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='contact_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='vendor_email',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='phone',
                size=50,
                required=True
            )

            time.sleep(5)

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='website',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='payment_terms',
                size=100,
                required=False
            )

            # Billing Address
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='billing_street',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='billing_city',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='enum',
                key='billing_state',
                elements=VENDOR_STATES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='billing_postal_code',
                size=20,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='billing_country',
                size=100,
                required=True
            )

            # Timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='created_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                attribute_type='string',
                key='updated_at',
                size=30,
                required=False
            )

            # Indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                key='vendor_email_index',
                type='key',
                attributes=['vendor_email'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                key='vendor_id_index',
                type='key',
                attributes=['vendor_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                key='user_id_idx',
                type='key',
                attributes=['user_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='vendors',
                key='phone_index',
                type='key',
                attributes=['phone'],
                orders=['ASC']
            )

            print("Created all vendor attributes and indexes")

        except Exception as e:
            print(f"Collection might already exist: {str(e)}")

        time.sleep(5)

        # Create products collection
        try:
            products = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='products',
                name='Products',
                permissions=['read("any")', 'write("any")']
            )
            print("Created products collection")

            # Required fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='product_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='float',
                key='price',
                required=True
            )

            # Add type field for products
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='type',
                size=20,
                default='product',
                required=False
            )

            # Physical product specific fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='integer',
                key='stock',
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='sku',
                size=50,
                required=True
            )

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='description',
                size=1000,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='string',
                key='category',
                array=True,
                size=100,
                required=False
            )

            # Timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='datetime',
                key='created_at',
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                attribute_type='datetime',
                key='updated_at',
                required=False
            )

            time.sleep(5)

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                key='user_id_idx',
                type='key',
                attributes=['user_id']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='products',
                key='sku_idx',
                type='key',
                attributes=['sku']
            )

            print("Created product attributes and indexes")

        except Exception as e:
            print(f"Error creating products collection: {str(e)}")

        time.sleep(5)

        # Create services collection
        try:
            services = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='services',
                name='Services',
                permissions=['read("any")', 'write("any")']
            )
            print("Created services collection")

            # Required fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='service_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='float',
                key='price',
                required=True
            )

            # Add type field for services
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='type',
                size=20,
                default='service',
                required=False
            )

            # Service specific fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='duration',
                size=50,
                required=False  # e.g., "1 hour", "30 minutes"
            )

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='description',
                size=1000,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='string',
                key='category',
                array=True,
                size=100,
                required=False
            )

            # Timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='datetime',
                key='created_at',
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                attribute_type='datetime',
                key='updated_at',
                required=False
            )

            time.sleep(5)

            # Create index
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='services',
                key='user_id_idx',
                type='key',
                attributes=['user_id']
            )

            print("Created service attributes and indexes")

        except Exception as e:
            print(f"Error creating services collection: {str(e)}")

        time.sleep(5)

        # Create estimates collection
        try:
            estimates = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='estimates',
                name='Estimates',
                permissions=['read("any")', 'write("any")']
            )
            print("Created estimates collection")

            # Basic estimate fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='estimate_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='estimate_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='expiry_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='customer_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='enum',
                key='status',
                elements=ESTIMATE_STATUSES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='line_items',
                size=1000000,  # Large size to accommodate JSON array
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='float',
                key='total',
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='enum',
                key='payment_terms',
                elements=ESTIMATE_PAYMENT_TERMS,
                required=True
            )

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='notes',
                size=1024,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='sent_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='accepted_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='declined_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='decline_reason',
                size=500,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                attribute_type='string',
                key='converted_at',
                size=30,
                required=False
            )

            time.sleep(5)

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                key='user_id_idx',
                type='key',
                attributes=['user_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                key='estimate_id_idx',
                type='key',
                attributes=['estimate_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                key='status_idx',
                type='key',
                attributes=['status'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='estimates',
                key='customer_id_idx',
                type='key',
                attributes=['customer_id'],
                orders=['ASC']
            )

            print("Created estimate attributes and indexes")

        except Exception as e:
            print(f"Error creating estimates collection: {str(e)}")

        time.sleep(5)

        # Create invoices collection
        try:
            invoices = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='invoices',
                name='Invoices',
                permissions=['read("any")', 'write("any")']
            )
            print("Created invoices collection")

            # Add user_id to invoices
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            # Invoice basic info
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='invoice_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='invoice_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='due_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='customer_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='enum',
                key='status',
                elements=INVOICE_STATUSES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='float',
                key='total',
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='float',
                key='amount_paid',
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='float',
                key='balance',
                required=True
            )

            # Store line items as JSON string
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='line_items',
                size=1000000,
                required=True
            )

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='notes',
                size=1024,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='enum',
                key='payment_terms',
                elements=INVOICE_PAYMENT_TERMS,
                required=True
            )

            # Status change timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='sent_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='accepted_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='declined_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='decline_reason',
                size=500,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='paid_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='voided_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='void_reason',
                size=500,
                required=False
            )

            # If this invoice was converted from an estimate
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='converted_from',
                size=50,
                required=False
            )

            # Record keeping timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='created_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='updated_at',
                size=30,
                required=False
            )

            time.sleep(2)

            # Create string attributes for invoices
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                attribute_type='string',
                key='payments',
                size=1000000,  # Large size for JSON string of payments
                required=False
            )

            time.sleep(5)

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                key='user_id_idx',
                type='key',
                attributes=['user_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                key='invoice_id_idx',
                type='key',
                attributes=['invoice_id'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                key='status_idx',
                type='key',
                attributes=['status'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                key='customer_id_idx',
                type='key',
                attributes=['customer_id'],
                orders=['ASC']
            )

            # Unique compound index
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='invoices',
                key='user_invoice_unique',
                type='unique',
                attributes=['user_id', 'invoice_id']
            )

            print("Created invoice attributes and indexes")

        except Exception as e:
            print(f"Error creating invoices collection: {str(e)}")

        time.sleep(5)

        # Create transactions collection
        try:
            transactions = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='transactions',
                name='Transactions',
                permissions=['read("any")', 'write("any")']
            )
            print("Created transactions collection")

            # Required fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='transaction_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='transaction_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='description',
                size=500,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='enum',
                key='status',
                elements=TRANSACTION_STATUSES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='enum',
                key='type',
                elements=TRANSACTION_TYPES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='float',
                key='total_amount',
                required=True
            )

            # Optional fields
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='notes',
                size=1000,
                required=False
            )

            # Timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='created_at',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='modified_at',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='posted_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='voided_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='void_reason',
                size=500,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                attribute_type='string',
                key='entries',
                size=1000000,
                required=True
            )

            time.sleep(5)

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                key='user_id_idx',
                type='key',
                attributes=['user_id']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='transactions',
                key='transaction_id_idx',
                type='key',
                attributes=['transaction_id']
            )

            print("Created transaction header attributes and indexes")

        except Exception as e:
            print(f"Error creating transaction collection: {str(e)}")

        time.sleep(5)

        # Create chart of accounts collection
        try:
            chart_of_accounts = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                name='Chart of Accounts',
                permissions=['read("any")', 'write("any")']
            )
            print("Created chart of accounts collection")

            # Chart of accounts attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='account_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='account_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='account_type',
                size=100,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='account_subtype',
                size=100,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='account_number',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='description',
                size=1000,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='boolean',
                key='is_active',
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='float',
                key='opening_balance',
                required=True,
                min=-1000000000,
                max=1000000000
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='float',
                key='current_balance',
                required=True,
                min=-1000000000,
                max=1000000000
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='created_at',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                attribute_type='string',
                key='updated_at',
                size=50,
                required=True
            )

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                key='user_id_idx',
                type='key',
                attributes=['user_id']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                key='account_id_idx',
                type='key',
                attributes=['account_id']
            )

            # Unique compound index
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                key='user_account_unique',
                type='unique',
                attributes=['user_id', 'account_id']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                key='account_number_index',
                type='unique',
                attributes=['account_number']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='chart_of_accounts',
                key='account_type_index',
                type='key',
                attributes=['account_type', 'account_subtype']
            )

            print("Completed chart of accounts collection setup")

        except Exception as e:
            print(
                f"Chart of accounts collection might already exist: {str(e)}")

        time.sleep(5)

        # Create purchase_orders collection
        try:
            purchase_orders = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                name='Purchase Orders',
                permissions=['read("any")', 'write("any")']
            )
            print("Created purchase_orders collection")

            # Purchase Order attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='po_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='po_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='due_date',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='vendor_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='enum',
                key='status',
                elements=PO_STATUSES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='enum',
                key='payment_terms',
                elements=PO_PAYMENT_TERMS,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='float',
                key='total',
                required=True,
                min=-999999999,
                max=999999999
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='float',
                key='amount_paid',
                required=True,
                min=-999999999,
                max=999999999
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='float',
                key='balance',
                required=True,
                min=-999999999,
                max=999999999
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='notes',
                size=1000,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='created_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='sent_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='accepted_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='declined_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='decline_reason',
                size=500,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='received_at',
                size=30,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                attribute_type='string',
                key='updated_at',
                size=30,
                required=False
            )

            # Create array attribute for line items
            databases.create_string_attribute(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                key='line_items',
                size=1000000,  # Adjust size as needed
                required=True
            )

            # Create indexes
            databases.create_index(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                key='user_vendor',
                type='key',
                attributes=['user_id', 'vendor_id']
            )

            databases.create_index(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                key='po_id',
                type='key',
                attributes=['po_id']
            )

            databases.create_index(
                database_id=DATABASE_ID,
                collection_id='purchase_orders',
                key='status',
                type='key',
                attributes=['status']
            )

            print("Created all purchase_orders attributes and indexes")

        except Exception as e:
            if e.code != 409:  # 409 means collection already exists
                raise e
            print("Purchase orders collection already exists")

        time.sleep(5)


        # Create company_settings collection
        try:
            company_settings = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                name='Company Settings',
                permissions=['read("users")'],
                document_security=True
            )
            print("Created company_settings collection")

            # Company Settings attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='legal_name',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='boolean',
                key='same_as_company_name',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='enum',
                key='identity_type',
                required=True,
                options=IDENTITY_TYPES
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='identity_number',
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='enum',
                key='tax_form',
                options=COMPANY_TAX_FORMS,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='enum',
                key='industry',
                options=INDUSTRY_TYPES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_email',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='customer_facing_email',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='boolean',
                key='same_as_company_email',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_phone',
                size=36
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='website',
                size=255,
                required=False
            )

            # Company Address
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_street',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_city',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='enum',
                key='company_state',
                elements=CUSTOMER_STATES,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_postal_code',
                size=20,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='company_country',
                size=100,
                required=True
            )

            # Legal Address
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='legal_street',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='legal_city',
                size=255,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='enum',
                key='legal_state',
                elements=CUSTOMER_STATES,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='legal_postal_code',
                size=20,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='legal_country',
                size=100,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='boolean',
                key='same_as_company_address',
                default=True,
                required=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='enum',
                key='status',
                enum=COMPANY_STATUS
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='created_at',
                size=255,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                attribute_type='string',
                key='updated_at',
                size=255,
                required=True
            )

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                key='user_unique',
                type='unique',
                attributes=['user_id'],
                orders=['asc']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                key='user_company',
                type='key',
                attributes=['user_id', 'company_name'],
                orders=['ASC', 'ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                key='company_status',
                type='key',
                attributes=['status'],
                orders=['ASC']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='company_settings',
                key='company_industry',
                type='key',
                attributes=['industry'],
                orders=['ASC']
            )

            print("Created company settings attributes and indexes")

        except Exception as e:
            if e.code != 409:  # 409 means collection already exists
                raise e
            print("Company Settings collection already exists")

        time.sleep(5)

        try:

            # Create advanced_settings collection
            advanced_settings = databases.create_collection(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                name='Advanced Settings',
                permissions=['read("users")'],
                document_security=True
            )
            print("Created advanced_settings collection")

            # Advanced Settings attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='user_id',
                size=50,
                required=True
            )

            # Accounting attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='fiscal_year_start',
                size=20,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='income_tax_year_start',
                size=20,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='accounting_method',
                size=50,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='close_the_books',
                default=False
            )

            # Company Type attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='tax_form',
                size=100,
                required=True
            )

            # Chart of Accounts attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='enable_account_numbers',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='tips_account',
                size=100,
                required=True
            )

            # Categories attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='track_classes',
                default=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='track_locations',
                default=False
            )

            # Automation attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='pre_fill_forms',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='apply_credits_automatically',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='invoice_unbilled_activity',
                default=False
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='apply_bill_payments_automatically',
                default=True
            )

            # Projects attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='organize_job_activity',
                default=False
            )

            # Currency attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='home_currency',
                size=10,
                default='USD'
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='multicurrency',
                default=False
            )

            # Other Preferences attributes
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='date_format',
                size=20,
                default='MM/DD/YYYY'
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='currency_format',
                size=20,
                default='$#,##0.00'
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='customer_label',
                size=50,
                default='Customer'
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='duplicate_check_warning',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='vendor_bill_warning',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='boolean',
                key='duplicate_journal_warning',
                default=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='sign_out_after_inactivity',
                size=20,
                default='3 hours'
            )

            # Timestamps
            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='created_at',
                size=30,
                required=True
            )

            create_attribute_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                attribute_type='string',
                key='updated_at',
                size=30,
                required=True
            )

            # Create indexes
            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                key='user_unique',
                type='unique',
                attributes=['user_id'],
                orders=['asc']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                key='accounting_method',
                type='key',
                attributes=['accounting_method']
            )

            create_index_with_retry(
                database_id=DATABASE_ID,
                collection_id='advanced_settings',
                key='home_currency',
                type='key',
                attributes=['home_currency']
            )
        except Exception as e:
            if e.code != 409:  # 409 means collection already exists
                raise e
            print("Advanced Settings collection already exists")

        time.sleep(5)
        print("\nSetup completed successfully!")
        print(f"Database ID: {DATABASE_ID}")
        print("Collection IDs: 'customers', 'products', 'services', 'estimates', 'invoices', 'transactions', 'chart_of_accounts', 'purchase_orders'")

    except Exception as e:
        print(f"Error setting up Appwrite: {str(e)}")


if __name__ == "__main__":
    setup_appwrite()
    sync_users_with_database()
