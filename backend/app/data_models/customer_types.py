# Customer status types
CUSTOMER_STATUS = [
    'active',           # Currently active customer
    'inactive',         # Inactive customer
    'blocked',          # Blocked due to various reasons
    'pending',          # Pending verification
    'archived'          # Archived/old customer
]

# Customer types
CUSTOMER_TYPES = [
    'individual',       # Individual customer
    'business',         # Business customer
    'government',       # Government entity
    'non_profit',       # Non-profit organization
    'reseller'          # Reseller customer
]

# US States for addresses
CUSTOMER_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

# Customer payment terms
CUSTOMER_PAYMENT_TERMS = [
    'due_on_receipt',        # Due immediately
    'net15',           # Due in 15 days
    'net30',           # Due in 30 days
    'net45',           # Due in 45 days
    'net60',           # Due in 60 days
    'custom'           # Custom payment terms
]
