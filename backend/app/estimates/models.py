from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

# Define valid estimate statuses
ESTIMATE_STATUSES = ["Draft", "Sent", "Accepted", "Declined"]

@dataclass
class Product:
    """Represents a product or service in an estimate"""
    name: str
    description: Optional[str] = ''
    price: float = 0.0
    quantity: int = 1
    type: str = 'service'
    sell_enabled: bool = True
    purchase_enabled: bool = False
    income_account_id: Optional[str] = None
    expense_account_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create a Product instance from a dictionary"""
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            price=float(data.get('price', 0.0)),
            quantity=int(data.get('quantity', 1)),
            type=data.get('type', 'service'),
            sell_enabled=data.get('sell_enabled', True),
            purchase_enabled=data.get('purchase_enabled', False),
            income_account_id=data.get('income_account_id'),
            expense_account_id=data.get('expense_account_id')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Product instance to dictionary"""
        data = {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'quantity': self.quantity,
            'type': self.type,
            'sell_enabled': self.sell_enabled,
            'purchase_enabled': self.purchase_enabled
        }
        if self.income_account_id:
            data['income_account_id'] = self.income_account_id
        if self.expense_account_id:
            data['expense_account_id'] = self.expense_account_id
        return data

@dataclass
class Estimate:
    """Represents an Estimate entry"""
    id: str
    estimate_no: str
    estimate_date: str
    customer_name: str
    status: str
    products: List[Product]
    total_amount: float
    accepted_by: Optional[str]
    accepted_date: Optional[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Estimate':
        """Create an Estimate instance from a dictionary"""
        now = datetime.utcnow().isoformat()
        products = [Product.from_dict(p) for p in data.get('products', [])]
        total_amount = sum(product.price * product.quantity for product in products)
        
        return cls(
            id=data.get('id', ''),
            estimate_no=data.get('estimate_no', ''),
            estimate_date=data.get('estimate_date', ''),
            customer_name=data.get('customer_name', ''),
            status=data.get('status', 'Draft'),
            products=products,
            total_amount=total_amount,
            accepted_by=data.get('accepted_by'),
            accepted_date=data.get('accepted_date'),
            created_at=data.get('created_at', now),
            updated_at=data.get('updated_at', now)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Estimate instance to dictionary"""
        data = {
            'id': self.id,
            'estimate_no': self.estimate_no,
            'estimate_date': self.estimate_date,
            'customer_name': self.customer_name,
            'status': self.status,
            'products': [p.to_dict() for p in self.products],
            'total_amount': self.total_amount,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self.accepted_by:
            data['accepted_by'] = self.accepted_by
        if self.accepted_date:
            data['accepted_date'] = self.accepted_date
        return data

@dataclass
class EstimatesSummary:
    """Summary information about estimates"""
    total_count: int = 0
    total_amount: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert EstimatesSummary instance to dictionary"""
        return {
            'total_count': self.total_count,
            'total_amount': self.total_amount
        }
