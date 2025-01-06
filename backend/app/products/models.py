from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import os
import json

# Product types
ITEM_TYPES = ["service", "inventory_item"]

# Default account IDs - these should match your chart of accounts
SALES_REVENUE_ID = "4000-0001"     # Sales Revenue
COGS_ID = "5000-0001"              # Cost of Goods Sold
INVENTORY_ASSET_ID = "1200-0001"   # Inventory Asset

# File path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DEFAULTS_DIR = os.path.join(DATA_DIR, 'defaults')
DEFAULT_PRODUCTS_FILE = os.path.join(DEFAULTS_DIR, 'products.json')

def get_user_products_file(user_id: str) -> str:
    """Get the products file path for a specific user"""
    user_dir = os.path.join(DATA_DIR, user_id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return os.path.join(user_dir, 'products.json')

def load_user_products(user_id: str) -> Dict:
    """Load products data from JSON file"""
    products_file = get_user_products_file(user_id)
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                return json.load(f)
        elif os.path.exists(DEFAULT_PRODUCTS_FILE):
            # If user file doesn't exist but default file does, copy it
            with open(DEFAULT_PRODUCTS_FILE, 'r') as f:
                data = json.load(f)
                # Save as user's file
                with open(products_file, 'w') as uf:
                    json.dump(data, uf, indent=2)
                return data
        return {'products': []}
    except Exception as e:
        print(f"Error loading products: {str(e)}")
        return {'products': []}

def save_user_products(user_id: str, data: Dict) -> bool:
    """Save products data to JSON file"""
    products_file = get_user_products_file(user_id)
    try:
        with open(products_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving products: {str(e)}")
        return False

@dataclass
class InventoryInfo:
    """Represents inventory information for inventory items"""
    quantity: float
    as_of_date: str
    inventory_asset_account_id: str = INVENTORY_ASSET_ID

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryInfo':
        """Create an InventoryInfo instance from a dictionary"""
        return cls(
            quantity=float(data.get('quantity', 0.0)),
            as_of_date=data.get('as_of_date', ''),
            inventory_asset_account_id=data.get('inventory_asset_account_id', INVENTORY_ASSET_ID)
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
    income_account_id: str = SALES_REVENUE_ID
    
    # Purchasing Information
    purchase_enabled: bool = False
    purchase_description: Optional[str] = None
    purchase_cost: float = 0.0
    expense_account_id: str = COGS_ID
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
            income_account_id = data.get('income_account_id', SALES_REVENUE_ID)
            expense_account_id = data.get('expense_account_id', COGS_ID)
            inventory_info = data.get('inventory_info')
            if inventory_info:
                inventory_info = InventoryInfo.from_dict(inventory_info)
        else:
            sell_enabled = data.get('sell_enabled', True)
            purchase_enabled = data.get('purchase_enabled', False)
            income_account_id = data.get('income_account_id', SALES_REVENUE_ID)
            expense_account_id = data.get('expense_account_id', COGS_ID)
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