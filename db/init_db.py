from sqlalchemy.orm import Session
from db.config import SessionLocal
from api.models.user_roles import UserRole
from api.models.users import User
from api.utils.hashing import hash_password
from core.config import settings

def seed_roles_and_admin():
    db: Session = SessionLocal()
    try:
        # Ensure roles
        role_admin = db.query(UserRole).filter(UserRole.name == "admin").first()
        if not role_admin:
            role_admin = UserRole(name="admin", description="Administrator")
            db.add(role_admin)

        role_employee = db.query(UserRole).filter(UserRole.name == "employee").first()
        if not role_employee:
            role_employee = UserRole(name="employee", description="Employee")
            db.add(role_employee)

        db.commit()
        db.refresh(role_admin)
        db.refresh(role_employee)

        # Ensure admin user
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        print("--- STARTING ADMIN PASSWORD DEBUG ---")
        print(f"Password Read from Settings: '{settings.ADMIN_PASSWORD}'")
        print(f"Length of Password Read: {len(settings.ADMIN_PASSWORD)}")
        print("-------------------------------------")
        if not admin:
            admin = User(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                full_name=settings.ADMIN_FULL_NAME,
                role_id=role_admin.id
            )
            db.add(admin)
            db.commit()
        print("Seed complete: roles + admin ready.")
    except Exception as e:
        db.rollback()
        print("Seed failed:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles_and_admin()
