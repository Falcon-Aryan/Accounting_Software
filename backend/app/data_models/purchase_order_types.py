# Purchase Order statuses and their transitions
PO_STATUSES = [
    'draft',           # Initial status when PO is created
    'sent',            # PO has been sent to vendor
    'accepted',        # Vendor has accepted the PO
    'declined',        # Vendor has declined the PO
    'partially_received', # Some items have been received
    'received',        # All items have been received
    'cancelled',       # PO has been cancelled
    'closed'           # PO is complete and closed
]

# Define valid status transitions
PO_STATUS_TRANSITIONS = {
    'draft': ['sent', 'cancelled'],
    'sent': ['accepted', 'declined', 'cancelled', 'draft'],
    'accepted': ['partially_received', 'received', 'cancelled', 'draft'],
    'declined': ['draft', 'cancelled'],
    'partially_received': ['received', 'cancelled', 'draft'],
    'received': ['closed', 'draft'],
    'cancelled': ['draft'],
    'closed': ['draft']  # No transitions from closed state
}

# Purchase Order Types
PO_TYPES = [
    'standard',          # Regular purchase order
    'blanket',           # Long-term agreement with multiple deliveries
    'contract',          # Formal contract-based PO
    'direct',           # Direct to vendor without quotation
    'emergency',        # Urgent/emergency purchases
]

# Payment Terms
PO_PAYMENT_TERMS = [
    'due_on_receipt',        # Due immediately
    'net15',           # Due in 15 days
    'net30',           # Due in 30 days
    'net45',           # Due in 45 days
    'net60',           # Due in 60 days
    'custom'           # Custom payment terms
]

# Line Item Types
PO_LINE_ITEM_TYPES = ['product']

# Line Item statuses
PO_LINE_ITEM_STATUSES = [
    'pending',           # Initial status
    'partially_received', # Some quantity received
    'received',          # All quantity received
    'cancelled'          # Line item cancelled
]

# Define valid line item status transitions
PO_LINE_ITEM_STATUS_TRANSITIONS = {
    'pending': ['partially_received', 'received', 'cancelled'],
    'partially_received': ['received', 'cancelled'],
    'received': [],  # No transitions from received state
    'cancelled': []  # No transitions from cancelled state
}