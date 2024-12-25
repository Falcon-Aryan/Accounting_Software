from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

# Product types
ITEM_TYPES = ["service", "inventory_item"]

@dataclass
class InventoryInfo:
    """Represents inventory information for inventory items"""
    quantity: float
    as_of_date: str
    inventory_asset_account_id: str = "Inventory Asset"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryInfo':
        """Create an InventoryInfo instance from a dictionary"""
        return cls(
            quantity=float(data.get('quantity', 0.0)),
            as_of_date=data.get('as_of_date', ''),
            inventory_asset_account_id=data.get('inventory_asset_account_id', 'Inventory Asset')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert InventoryInfo instance to dictionary"""
        return {
            'quantity': self.quantity,
            'as_of_date': self.as_of_date,
            'inventory_asset_account_id': self.inventory_asset_account_id
        }

@dataclass
class Product:
    """Represents a product or service"""
    id: str
    name: str
    type: str
    sku: Optional[str]
    category: Optional[str]
    
    # Sales Information
    sell_enabled: bool = True
    description: Optional[str] = None
    unit_price: float = 0.0
    cost_price: Optional[float] = None
    income_account_id: str = "4000-0001"  # Default Sales Revenue ID
    
    # Purchasing Information
    purchase_enabled: bool = False
    purchase_description: Optional[str] = None
    purchase_cost: float = 0.0
    expense_account_id: str = "5000-0001"  # Default COGS ID
    preferred_vendor_id: Optional[str] = None
    
    # Inventory Information (only for inventory items)
    inventory_info: Optional[InventoryInfo] = None
    
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create a Product instance from a dictionary"""
        now = datetime.utcnow().isoformat()
        
        # Set defaults based on type
        item_type = data.get('type', 'service')
        if item_type == 'inventory_item':
            sell_enabled = True
            purchase_enabled = True
            income_account_id = data.get('income_account_id', '4000-0001')  # Default Sales Revenue ID
            expense_account_id = data.get('expense_account_id', '5000-0001')  # Default COGS ID
            inventory_info = data.get('inventory_info')
            if inventory_info:
                inventory_info = InventoryInfo.from_dict(inventory_info)
        else:
            sell_enabled = data.get('sell_enabled', True)
            purchase_enabled = data.get('purchase_enabled', False)
            income_account_id = data.get('income_account_id', '4000-0001')  # Default Sales Revenue ID
            expense_account_id = data.get('expense_account_id', '5000-0001')  # Default COGS ID
            inventory_info = None
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            type=item_type,
            sku=data.get('sku'),
            category=data.get('category'),
            sell_enabled=sell_enabled,
            description=data.get('description'),
            unit_price=float(data.get('unit_price', 0.0)),
            cost_price=float(data.get('cost_price', 0.0)) if data.get('cost_price') is not None else None,
            income_account_id=income_account_id,
            purchase_enabled=purchase_enabled,
            purchase_description=data.get('purchase_description'),
            purchase_cost=float(data.get('purchase_cost', 0.0)),
            expense_account_id=expense_account_id,
            preferred_vendor_id=data.get('preferred_vendor_id'),
            inventory_info=inventory_info,
            created_at=data.get('created_at', now),
            updated_at=data.get('updated_at', now)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Product instance to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'sell_enabled': self.sell_enabled,
            'income_account_id': self.income_account_id,
            'purchase_enabled': self.purchase_enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Add expense account only if purchase is enabled
        if self.purchase_enabled:
            data['expense_account_id'] = self.expense_account_id
        
        # Add optional fields if they exist
        if self.sku:
            data['sku'] = self.sku
        if self.category:
            data['category'] = self.category
        if self.description:
            data['description'] = self.description
        if self.unit_price:
            data['unit_price'] = self.unit_price
        if self.cost_price is not None:
            data['cost_price'] = self.cost_price
        if self.purchase_description:
            data['purchase_description'] = self.purchase_description
        if self.purchase_cost:
            data['purchase_cost'] = self.purchase_cost
        if self.preferred_vendor_id:
            data['preferred_vendor_id'] = self.preferred_vendor_id
        if self.inventory_info:
            data['inventory_info'] = self.inventory_info.to_dict()
            
        return data

@dataclass
class ProductsSummary:
    """Summary information about products"""
    total_count: int = 0
    service_count: int = 0
    inventory_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ProductsSummary instance to dictionary"""
        return {
            'total_count': self.total_count,
            'service_count': self.service_count,
            'inventory_count': self.inventory_count
        }
