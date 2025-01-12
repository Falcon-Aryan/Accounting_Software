from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class LineItem:
    """Line item for both estimates and invoices"""
    product_id: str
    quantity: float = 1.0
    unit_price: float = 0.0
    description: Optional[str] = None
    total: float = 0.0

    def __post_init__(self):
        self.total = self.quantity * self.unit_price

    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'description': self.description,
            'total': self.total
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LineItem':
        return cls(
            product_id=data['product_id'],
            quantity=float(data.get('quantity', 1.0)),
            unit_price=float(data.get('unit_price', 0.0)),
            description=data.get('description'),
            total=float(data.get('total', 0.0))
        )

@dataclass
class BaseDocument:
    """Base class for estimates and invoices"""
    id: str
    customer_id: str
    date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payment_terms: str = "due_on_receipt"
    status: str = "draft"
    line_items: List[LineItem] = field(default_factory=list)
    subtotal: float = 0.0
    total: float = 0.0
    notes: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        self._calculate_totals()

    def _calculate_totals(self):
        self.subtotal = sum(item.total for item in self.line_items)
        self.total = self.subtotal  # Can be extended for taxes/discounts

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'date': self.date,
            'payment_terms': self.payment_terms,
            'status': self.status,
            'line_items': [item.to_dict() for item in self.line_items],
            'subtotal': self.subtotal,
            'total': self.total,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseDocument':
        return cls(
            id=data['id'],
            customer_id=data['customer_id'],
            date=data.get('date'),
            payment_terms=data.get('payment_terms', 'due_on_receipt'),
            status=data.get('status', 'draft'),
            line_items=[LineItem.from_dict(item) for item in data.get('line_items', [])],
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )