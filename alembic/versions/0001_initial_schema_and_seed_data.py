"""initial_schema_and_seed_data

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-20 12:00:00.000000

"""
from typing import Sequence, Union
import warnings
import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from decimal import Decimal

# Suppress bcrypt version warning (compatibility issue between passlib and newer bcrypt)
warnings.filterwarnings("ignore", category=UserWarning, module="passlib.handlers.bcrypt")
# Also suppress at logging level
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Import your ORM models
from api.models.user_roles import UserRole
from api.models.users import User
from api.models.categories import Category
from api.models.assets import Asset
from api.models.assets_histories import AssetHistory
from api.utils.enums import AssetStatus
from api.utils.hashing import hash_password

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create all tables and seed initial data."""
    bind = op.get_bind()
    session = Session(bind=bind)

    # -----------------------------
    # 1. Create CITEXT extension
    # -----------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    # -----------------------------
    # 2. Create asset_status enum
    # -----------------------------
    # Drop enum if it exists (for fresh database setup - safe since DB is blank)
    op.execute("DROP TYPE IF EXISTS asset_status CASCADE")
    # Create the enum type manually first
    op.execute("CREATE TYPE asset_status AS ENUM ('available', 'assigned', 'under_repair', 'damaged')")
    # Create enum object for use in table definitions
    # Using create_type=False prevents SQLAlchemy from trying to create it again
    asset_status_enum = postgresql.ENUM(
        'available', 'assigned', 'under_repair', 'damaged',
        name='asset_status',
        create_type=False
    )

    # -----------------------------
    # 3. Create user_roles table
    # -----------------------------
    op.create_table('user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=False)

    # -----------------------------
    # 4. Create users table
    # -----------------------------
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', postgresql.CITEXT(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('employee_code', sa.Text(), nullable=True),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['user_roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('employee_code')
    )

    # -----------------------------
    # 5. Create password_reset_tokens table
    # -----------------------------
    op.create_table('password_reset_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('used_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    # -----------------------------
    # 6. Create categories table
    # -----------------------------
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)

    # -----------------------------
    # 7. Create assets table
    # -----------------------------
    op.create_table('assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('tag_code', sa.Text(), nullable=True),
        sa.Column('serial_number', sa.Text(), nullable=True),
        sa.Column('status', asset_status_enum, server_default='available', nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('warranty_expiry', sa.Date(), nullable=True),
        sa.Column('specs', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_number'),
        sa.UniqueConstraint('tag_code')
    )

    # -----------------------------
    # 8. Create allocations table
    # -----------------------------
    op.create_table('allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allocated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allocation_date', sa.Date(), nullable=False),
        sa.Column('returned_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['allocated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('uq_open_allocation_per_asset', 'allocations', ['asset_id'], unique=True, postgresql_where=sa.text('returned_at IS NULL'))
    op.create_index('idx_alloc_employee_open', 'allocations', ['employee_id'], postgresql_where=sa.text('returned_at IS NULL'))

    # -----------------------------
    # 9. Create assets_histories table
    # -----------------------------
    op.create_table('assets_histories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('from_status', asset_status_enum, nullable=True),
        sa.Column('to_status', asset_status_enum, nullable=False),
        sa.Column('event_metadata', sa.JSON(), nullable=True),
        sa.Column('occurred_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # -----------------------------
    # 10. Create return_requests table
    # -----------------------------
    op.create_table('return_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allocation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('decision_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['allocation_id'], ['allocations.id'], ),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_return_requests_pending', 'return_requests', ['id'], postgresql_where=sa.text('approved_at IS NULL'))

    # -----------------------------
    # 11. SEED DATA: Insert Roles (2 roles)
    # -----------------------------
    admin_role = UserRole(
        id=1,
        name="admin",
        description="Administrator with full system access",
        created_at=datetime.now(timezone.utc)
    )
    employee_role = UserRole(
        id=2,
        name="employee",
        description="Regular employee user",
        created_at=datetime.now(timezone.utc)
    )

    session.add_all([admin_role, employee_role])
    session.flush()

    # -----------------------------
    # 12. SEED DATA: Insert Users (1 admin + 4 employees)
    # UUIDs will be auto-generated by SQLAlchemy
    # -----------------------------
    password_hash = hash_password("password123")  # Default password for all test users

    users = [
        # Admin user
        User(
            email="admin@company.com",
            password_hash=password_hash,
            full_name="Admin User",
            role_id=1,  # admin role
            employee_code="ADM001",
            phone="9876500001",
            created_at=datetime.now(timezone.utc),
        ),
        # Employee users (4)
        User(
            email="john.doe@company.com",
            password_hash=password_hash,
            full_name="John Doe",
            role_id=2,  # employee role
            employee_code="EMP001",
            phone="9876500002",
            created_at=datetime.now(timezone.utc),
        ),
        User(
            email="sarah.smith@company.com",
            password_hash=password_hash,
            full_name="Sarah Smith",
            role_id=2,  # employee role
            employee_code="EMP002",
            phone="9876500003",
            created_at=datetime.now(timezone.utc),
        ),
        User(
            email="mike.johnson@company.com",
            password_hash=password_hash,
            full_name="Mike Johnson",
            role_id=2,  # employee role
            employee_code="EMP003",
            phone="9876500004",
            created_at=datetime.now(timezone.utc),
        ),
        User(
            email="emily.brown@company.com",
            password_hash=password_hash,
            full_name="Emily Brown",
            role_id=2,  # employee role
            employee_code="EMP004",
            phone="9876500005",
            created_at=datetime.now(timezone.utc),
        ),
    ]

    session.add_all(users)
    session.flush()

    # -----------------------------
    # 13. SEED DATA: Insert Categories (5 categories)
    # -----------------------------
    categories = [
        Category(
            id=1,
            name="Laptops",
            description="Portable computers and laptops",
            created_at=datetime.now(timezone.utc)
        ),
        Category(
            id=2,
            name="Monitors",
            description="Computer monitors and displays",
            created_at=datetime.now(timezone.utc)
        ),
        Category(
            id=3,
            name="Keyboards",
            description="Computer keyboards and input devices",
            created_at=datetime.now(timezone.utc)
        ),
        Category(
            id=4,
            name="Mice",
            description="Computer mice and pointing devices",
            created_at=datetime.now(timezone.utc)
        ),
        Category(
            id=5,
            name="Headphones",
            description="Audio headphones and headsets",
            created_at=datetime.now(timezone.utc)
        ),
    ]

    session.add_all(categories)
    session.flush()

    # -----------------------------
    # 14. SEED DATA: Insert Assets (12 assets)
    # 7 available, 3 under_repair, 2 damaged
    # UUIDs will be auto-generated by SQLAlchemy
    # -----------------------------
    assets = [
        # Available assets (7)
        Asset(
            category_id=1,
            name="Dell XPS 15 Laptop",
            tag_code="LAP-001",
            serial_number="DLXPS15001",
            status=AssetStatus.available,
            purchase_date=date(2024, 1, 15),
            purchase_cost=Decimal("1299.99"),
            warranty_expiry=date(2027, 1, 15),
            specs={"ram": "16GB", "storage": "512GB SSD", "processor": "Intel i7"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=1,
            name="MacBook Pro 14",
            tag_code="LAP-002",
            serial_number="MBP14002",
            status=AssetStatus.available,
            purchase_date=date(2024, 2, 20),
            purchase_cost=Decimal("1999.99"),
            warranty_expiry=date(2027, 2, 20),
            specs={"ram": "16GB", "storage": "1TB SSD", "processor": "M2 Pro"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=2,
            name="LG UltraWide Monitor 34",
            tag_code="MON-001",
            serial_number="LGUW34001",
            status=AssetStatus.available,
            purchase_date=date(2024, 3, 10),
            purchase_cost=Decimal("499.99"),
            warranty_expiry=date(2027, 3, 10),
            specs={"resolution": "3440x1440", "refresh_rate": "144Hz", "panel": "IPS"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=2,
            name="Dell 27-inch 4K Monitor",
            tag_code="MON-002",
            serial_number="DL27K002",
            status=AssetStatus.available,
            purchase_date=date(2024, 4, 5),
            purchase_cost=Decimal("399.99"),
            warranty_expiry=date(2027, 4, 5),
            specs={"resolution": "3840x2160", "refresh_rate": "60Hz", "panel": "IPS"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=3,
            name="Mechanical Keyboard RGB",
            tag_code="KEY-001",
            serial_number="MKRGB001",
            status=AssetStatus.available,
            purchase_date=date(2024, 5, 12),
            purchase_cost=Decimal("149.99"),
            warranty_expiry=date(2026, 5, 12),
            specs={"switch_type": "Cherry MX Blue", "layout": "Full Size", "backlight": "RGB"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=4,
            name="Logitech MX Master 3",
            tag_code="MOU-001",
            serial_number="LGMX3001",
            status=AssetStatus.available,
            purchase_date=date(2024, 6, 18),
            purchase_cost=Decimal("99.99"),
            warranty_expiry=date(2026, 6, 18),
            specs={"dpi": "4000", "connectivity": "Wireless", "battery": "Rechargeable"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=5,
            name="Sony WH-1000XM5 Headphones",
            tag_code="HP-001",
            serial_number="SNWHXM5001",
            status=AssetStatus.available,
            purchase_date=date(2024, 7, 22),
            purchase_cost=Decimal("399.99"),
            warranty_expiry=date(2026, 7, 22),
            specs={"noise_cancelling": "Yes", "battery_life": "30 hours", "connectivity": "Bluetooth"},
            created_at=datetime.now(timezone.utc)
        ),
        
        # Under repair assets (3)
        Asset(
            category_id=1,
            name="HP EliteBook 840",
            tag_code="LAP-003",
            serial_number="HPEL84001",
            status=AssetStatus.under_repair,
            purchase_date=date(2023, 8, 10),
            purchase_cost=Decimal("1099.99"),
            warranty_expiry=date(2026, 8, 10),
            specs={"ram": "8GB", "storage": "256GB SSD", "processor": "Intel i5"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=2,
            name="Samsung 32-inch Curved Monitor",
            tag_code="MON-003",
            serial_number="SM32C003",
            status=AssetStatus.under_repair,
            purchase_date=date(2023, 9, 15),
            purchase_cost=Decimal("349.99"),
            warranty_expiry=date(2026, 9, 15),
            specs={"resolution": "2560x1440", "refresh_rate": "144Hz", "panel": "VA"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=3,
            name="Wireless Keyboard",
            tag_code="KEY-002",
            serial_number="WLKB002",
            status=AssetStatus.under_repair,
            purchase_date=date(2023, 10, 20),
            purchase_cost=Decimal("79.99"),
            warranty_expiry=date(2025, 10, 20),
            specs={"connectivity": "Wireless", "layout": "Full Size", "battery": "AA x2"},
            created_at=datetime.now(timezone.utc)
        ),
        
        # Damaged assets (2)
        Asset(
            category_id=4,
            name="Gaming Mouse RGB",
            tag_code="MOU-002",
            serial_number="GMRGB002",
            status=AssetStatus.damaged,
            purchase_date=date(2023, 11, 5),
            purchase_cost=Decimal("59.99"),
            warranty_expiry=date(2025, 11, 5),
            specs={"dpi": "12000", "connectivity": "Wired", "buttons": "7"},
            created_at=datetime.now(timezone.utc)
        ),
        Asset(
            category_id=5,
            name="Bose QuietComfort 45",
            tag_code="HP-002",
            serial_number="BQCF45002",
            status=AssetStatus.damaged,
            purchase_date=date(2023, 12, 12),
            purchase_cost=Decimal("329.99"),
            warranty_expiry=date(2025, 12, 12),
            specs={"noise_cancelling": "Yes", "battery_life": "24 hours", "connectivity": "Bluetooth"},
            created_at=datetime.now(timezone.utc)
        ),
    ]

    session.add_all(assets)
    session.commit()


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index('idx_return_requests_pending', table_name='return_requests')
    op.drop_table('return_requests')
    op.drop_table('assets_histories')
    op.drop_index('idx_alloc_employee_open', table_name='allocations')
    op.drop_index('uq_open_allocation_per_asset', table_name='allocations')
    op.drop_table('allocations')
    op.drop_table('assets')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_table('password_reset_tokens')
    op.drop_table('users')
    op.drop_index(op.f('ix_user_roles_id'), table_name='user_roles')
    op.drop_table('user_roles')
    
    # Drop enum (if exists)
    op.execute("DROP TYPE IF EXISTS asset_status")

