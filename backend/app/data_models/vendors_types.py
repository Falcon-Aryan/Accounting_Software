# Vendor status types
VENDOR_STATUS = [
    'active',           # Currently active vendor
    'inactive',         # Inactive vendor
    'blocked',          # Blocked vendor
    'pending',          # Pending verification
    'archived'          # Archived vendor
]

# Vendor types
VENDOR_TYPES = [
    'supplier',         # Product supplier
    'contractor',       # Service contractor
    'consultant',       # Professional consultant
    'manufacturer',     # Product manufacturer
    'distributor'       # Product distributor
]

# US States for addresses
VENDOR_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

# Vendor payment terms
VENDOR_PAYMENT_TERMS = [
    'due_on_receipt',        # Due immediately
    'net15',           # Due in 15 days
    'net30',           # Due in 30 days
    'net45',           # Due in 45 days
    'net60',           # Due in 60 days
    'custom'           # Custom payment terms
]
