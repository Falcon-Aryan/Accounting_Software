# Estimate status types
ESTIMATE_STATUSES = [
    'draft',           # Initial draft
    'sent',            # Sent to customer
    'accepted',        # Customer accepted
    'declined',        # Customer declined
    'expired',         # Estimate expired
    'converted',       # Converted to invoice
    'cancelled'        # Cancelled estimate
]

# Status transitions
ESTIMATE_STATUS_TRANSITIONS = {
    'draft': ['sent', 'cancelled'],
    'sent': ['accepted', 'declined', 'expired', 'cancelled', 'draft'],
    'accepted': ['converted', 'cancelled', 'draft'],
    'declined': ['draft', 'cancelled'],
    'expired': ['draft', 'cancelled'],
    'converted': ['draft'],   # End state
    'cancelled': ['draft']
}

# Estimate payment terms
ESTIMATE_PAYMENT_TERMS = [
    'due_on_receipt',       # Due immediately
    'net15',          # Due in 15 days
    'net30',          # Due in 30 days
    'net45',          # Due in 45 days
    'net60',          # Due in 60 days
    'custom'          # Custom payment terms
]
