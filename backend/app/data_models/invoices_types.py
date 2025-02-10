# Invoice status types
INVOICE_STATUSES = [
    'draft',            # Initial draft
    'sent',             # Sent to customer
    'accepted',         # Customer accepted
    'declined',         # Customer declined
    'paid',            # Fully paid
    'partially_paid',  # Partially paid
    'overdue',         # Payment overdue
    'cancelled',       # Cancelled invoice
    'void'             # Voided invoice
]

# Status transitions
INVOICE_STATUS_TRANSITIONS = {
    'draft': ['sent', 'cancelled'],
    'sent': ['accepted', 'declined', 'partial_payment', 'paid', 'overdue', 'cancelled', 'draft'],
    'accepted': ['partial_payment', 'paid', 'overdue', 'cancelled', 'draft'],
    'declined': ['draft', 'cancelled'],
    'partial_payment': ['paid', 'overdue', 'void', 'draft'],
    'paid': ['void', 'draft'],
    'overdue': ['partial_payment', 'paid', 'void', 'draft'],
    'cancelled': ['draft'],
    'void': ['draft']         # End state
}

# Invoice payment terms
INVOICE_PAYMENT_TERMS = [
    'due_on_receipt',       # Due immediately
    'net15',          # Due in 15 days
    'net30',          # Due in 30 days
    'net45',          # Due in 45 days
    'net60',          # Due in 60 days
    'custom'          # Custom payment terms
]

# Invoice payment methods
INVOICE_PAYMENT_METHODS = [
    'cash',           # Cash payment
    'check',          # Check payment
    'credit_card',    # Credit card payment
    'bank_transfer',  # Bank transfer
    'wire_transfer',  # Wire transfer
    'other'           # Other payment methods
]