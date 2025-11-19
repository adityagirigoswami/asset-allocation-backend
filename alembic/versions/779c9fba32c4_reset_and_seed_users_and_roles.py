"""Reset and seed users and user_roles"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

# Import your ORM models
from api.models.users import User
from api.models.user_roles import UserRole
from api.utils.hashing import hash_password

# IMPORTANT: Fixed revision ID and down_revision to resolve branching issue
revision = '779c9fba32c4'
down_revision = '642f88b332ad'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # -----------------------------
    # 1. DELETE existing data (in FK-safe order)
    # -----------------------------
    session.query(User).delete()
    session.query(UserRole).delete()
    session.flush()

    # -----------------------------
    # 2. Insert Roles
    # -----------------------------
    admin_role = UserRole(
        id=1,
        name="admin",
        description="Administrator",
        created_at=datetime.utcnow()
    )
    employee_role = UserRole(
        id=2,
        name="employee",
        description="Employee",
        created_at=datetime.utcnow()
    )

    session.add_all([admin_role, employee_role])
    session.flush()

    # -----------------------------
    # 3. Insert Users with BCRYPT hash
    # -----------------------------
    password_hash = hash_password("password123")

    users = [
        User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="admin@company.com",
            password_hash=password_hash,
            full_name="Admin User",
            role_id=1,
            employee_code="EMP001",
            phone="9876500001",
            created_at=datetime.utcnow(),
        ),
        User(
            id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            email="john.doe@company.com",
            password_hash=password_hash,
            full_name="John Doe",
            role_id=2,
            employee_code="EMP002",
            phone="9876500002",
            created_at=datetime.utcnow(),
        ),
        User(
            id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            email="sarah.smith@company.com",
            password_hash=password_hash,
            full_name="Sarah Smith",
            role_id=2,
            employee_code="EMP003",
            phone="9876500003",
            created_at=datetime.utcnow(),
        ),
    ]

    session.add_all(users)
    session.commit()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    session.query(User).delete()
    session.query(UserRole).delete()
    session.commit()
