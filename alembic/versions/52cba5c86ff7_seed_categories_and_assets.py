"""seed_categories_and_assets

Revision ID: 52cba5c86ff7
Revises: 779c9fba32c4
Create Date: 2025-11-19 11:10:23.044890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
from decimal import Decimal

# Import your ORM models
from api.models.categories import Category
from api.models.assets import Asset
from api.utils.enums import AssetStatus

# revision identifiers, used by Alembic.
revision: str = '52cba5c86ff7'
down_revision: Union[str, Sequence[str], None] = '779c9fba32c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    # -----------------------------
    # 1. Insert Categories (5 sample categories)
    # -----------------------------
    categories = [
        Category(
            id=1,
            name="Laptops",
            description="Portable computers and laptops",
            created_at=datetime.utcnow()
        ),
        Category(
            id=2,
            name="Monitors",
            description="Computer monitors and displays",
            created_at=datetime.utcnow()
        ),
        Category(
            id=3,
            name="Keyboards",
            description="Computer keyboards and input devices",
            created_at=datetime.utcnow()
        ),
        Category(
            id=4,
            name="Mice",
            description="Computer mice and pointing devices",
            created_at=datetime.utcnow()
        ),
        Category(
            id=5,
            name="Headphones",
            description="Audio headphones and headsets",
            created_at=datetime.utcnow()
        ),
    ]

    session.add_all(categories)
    session.flush()

    # -----------------------------
    # 2. Insert Assets (12 sample assets)
    # -----------------------------
    # 7 assets with status "available"
    # 3 assets with status "under_repair"
    # 2 assets with status "damaged"
    
    assets = [
        # Available assets (7)
        Asset(
            id=uuid.UUID("aaaaaaaa-1111-1111-1111-111111111111"),
            category_id=1,
            name="Dell XPS 15 Laptop",
            tag_code="LAP-001",
            serial_number="DLXPS15001",
            status=AssetStatus.available,
            purchase_date=date(2024, 1, 15),
            purchase_cost=Decimal("1299.99"),
            warranty_expiry=date(2027, 1, 15),
            specs={"ram": "16GB", "storage": "512GB SSD", "processor": "Intel i7"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("aaaaaaaa-2222-2222-2222-222222222222"),
            category_id=1,
            name="MacBook Pro 14",
            tag_code="LAP-002",
            serial_number="MBP14002",
            status=AssetStatus.available,
            purchase_date=date(2024, 2, 20),
            purchase_cost=Decimal("1999.99"),
            warranty_expiry=date(2027, 2, 20),
            specs={"ram": "16GB", "storage": "1TB SSD", "processor": "M2 Pro"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("aaaaaaaa-3333-3333-3333-333333333333"),
            category_id=2,
            name="LG UltraWide Monitor 34",
            tag_code="MON-001",
            serial_number="LGUW34001",
            status=AssetStatus.available,
            purchase_date=date(2024, 3, 10),
            purchase_cost=Decimal("499.99"),
            warranty_expiry=date(2027, 3, 10),
            specs={"resolution": "3440x1440", "refresh_rate": "144Hz", "panel": "IPS"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("aaaaaaaa-4444-4444-4444-444444444444"),
            category_id=2,
            name="Dell 27-inch 4K Monitor",
            tag_code="MON-002",
            serial_number="DL27K002",
            status=AssetStatus.available,
            purchase_date=date(2024, 4, 5),
            purchase_cost=Decimal("399.99"),
            warranty_expiry=date(2027, 4, 5),
            specs={"resolution": "3840x2160", "refresh_rate": "60Hz", "panel": "IPS"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("aaaaaaaa-5555-5555-5555-555555555555"),
            category_id=3,
            name="Mechanical Keyboard RGB",
            tag_code="KEY-001",
            serial_number="MKRGB001",
            status=AssetStatus.available,
            purchase_date=date(2024, 5, 12),
            purchase_cost=Decimal("149.99"),
            warranty_expiry=date(2026, 5, 12),
            specs={"switch_type": "Cherry MX Blue", "layout": "Full Size", "backlight": "RGB"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("aaaaaaaa-6666-6666-6666-666666666666"),
            category_id=4,
            name="Logitech MX Master 3",
            tag_code="MOU-001",
            serial_number="LGMX3001",
            status=AssetStatus.available,
            purchase_date=date(2024, 6, 18),
            purchase_cost=Decimal("99.99"),
            warranty_expiry=date(2026, 6, 18),
            specs={"dpi": "4000", "connectivity": "Wireless", "battery": "Rechargeable"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("aaaaaaaa-7777-7777-7777-777777777777"),
            category_id=5,
            name="Sony WH-1000XM5 Headphones",
            tag_code="HP-001",
            serial_number="SNWHXM5001",
            status=AssetStatus.available,
            purchase_date=date(2024, 7, 22),
            purchase_cost=Decimal("399.99"),
            warranty_expiry=date(2026, 7, 22),
            specs={"noise_cancelling": "Yes", "battery_life": "30 hours", "connectivity": "Bluetooth"},
            created_at=datetime.utcnow()
        ),
        
        # Under repair assets (3)
        Asset(
            id=uuid.UUID("bbbbbbbb-1111-1111-1111-111111111111"),
            category_id=1,
            name="HP EliteBook 840",
            tag_code="LAP-003",
            serial_number="HPEL84001",
            status=AssetStatus.under_repair,
            purchase_date=date(2023, 8, 10),
            purchase_cost=Decimal("1099.99"),
            warranty_expiry=date(2026, 8, 10),
            specs={"ram": "8GB", "storage": "256GB SSD", "processor": "Intel i5"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("bbbbbbbb-2222-2222-2222-222222222222"),
            category_id=2,
            name="Samsung 32-inch Curved Monitor",
            tag_code="MON-003",
            serial_number="SM32C003",
            status=AssetStatus.under_repair,
            purchase_date=date(2023, 9, 15),
            purchase_cost=Decimal("349.99"),
            warranty_expiry=date(2026, 9, 15),
            specs={"resolution": "2560x1440", "refresh_rate": "144Hz", "panel": "VA"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("bbbbbbbb-3333-3333-3333-333333333333"),
            category_id=3,
            name="Wireless Keyboard",
            tag_code="KEY-002",
            serial_number="WLKB002",
            status=AssetStatus.under_repair,
            purchase_date=date(2023, 10, 20),
            purchase_cost=Decimal("79.99"),
            warranty_expiry=date(2025, 10, 20),
            specs={"connectivity": "Wireless", "layout": "Full Size", "battery": "AA x2"},
            created_at=datetime.utcnow()
        ),
        
        # Damaged assets (2)
        Asset(
            id=uuid.UUID("cccccccc-1111-1111-1111-111111111111"),
            category_id=4,
            name="Gaming Mouse RGB",
            tag_code="MOU-002",
            serial_number="GMRGB002",
            status=AssetStatus.damaged,
            purchase_date=date(2023, 11, 5),
            purchase_cost=Decimal("59.99"),
            warranty_expiry=date(2025, 11, 5),
            specs={"dpi": "12000", "connectivity": "Wired", "buttons": "7"},
            created_at=datetime.utcnow()
        ),
        Asset(
            id=uuid.UUID("cccccccc-2222-2222-2222-222222222222"),
            category_id=5,
            name="Bose QuietComfort 45",
            tag_code="HP-002",
            serial_number="BQCF45002",
            status=AssetStatus.damaged,
            purchase_date=date(2023, 12, 12),
            purchase_cost=Decimal("329.99"),
            warranty_expiry=date(2025, 12, 12),
            specs={"noise_cancelling": "Yes", "battery_life": "24 hours", "connectivity": "Bluetooth"},
            created_at=datetime.utcnow()
        ),
    ]

    session.add_all(assets)
    session.commit()


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    session = Session(bind=bind)

    # Delete seeded data in FK-safe order
    session.query(Asset).delete()
    session.query(Category).delete()
    session.commit()
