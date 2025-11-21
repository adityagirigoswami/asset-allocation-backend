"""Basic tests for Pydantic schemas"""
import pytest
from datetime import date
from pydantic import ValidationError
from api.schemas.user_schemas import EmployeeCreate, UserLogin, UserUpdate
from api.schemas.asset_schemas import AssetCreate, AssetUpdate, CategoryCreate
from api.utils.enums import AssetStatus


class TestUserSchemas:
    """Test user-related schemas"""
    
    def test_employee_create_valid(self):
        """Test valid employee creation schema"""
        data = {
            "email": "employee@example.com",
            "password": "password123",
            "full_name": "John Doe",
            "employee_code": "EMP001",
            "phone": "1234567890"
        }
        schema = EmployeeCreate(**data)
        assert schema.email == "employee@example.com"
        assert schema.full_name == "John Doe"
        assert schema.employee_code == "EMP001"
    
    def test_employee_create_invalid_email(self):
        """Test employee creation with invalid email"""
        with pytest.raises(ValidationError):
            EmployeeCreate(
                email="invalid-email",
                password="password123",
                full_name="Test User"
            )
    
    def test_user_login_valid(self):
        """Test valid login schema"""
        data = {
            "email": "user@example.com",
            "password": "password123"
        }
        schema = UserLogin(**data)
        assert schema.email == "user@example.com"
        assert schema.password == "password123"
    
    def test_user_update_partial(self):
        """Test user update with partial data"""
        data = {"full_name": "Updated Name"}
        schema = UserUpdate(**data)
        assert schema.full_name == "Updated Name"
        assert schema.password is None
        assert schema.employee_code is None
    
    def test_employee_create_missing_required_fields(self):
        """Test employee creation with missing required fields"""
        # Missing email (required field)
        with pytest.raises(ValidationError) as exc_info:
            EmployeeCreate(
                password="password123",
                full_name="Test User"
            )
        # Should raise validation error for missing email
        assert "email" in str(exc_info.value).lower()
    
    def test_user_login_missing_password(self):
        """Test user login with missing password"""
        # Missing password (required field)
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(email="user@example.com")
        # Should raise validation error for missing password
        assert "password" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


class TestAssetSchemas:
    """Test asset-related schemas"""
    
    def test_asset_create_valid(self):
        """Test valid asset creation schema"""
        data = {
            "category_id": 1,
            "name": "Test Laptop",
            "tag_code": "LAP-001",
            "status": "available"
        }
        schema = AssetCreate(**data)
        assert schema.name == "Test Laptop"
        assert schema.category_id == 1
        assert schema.status == AssetStatus.available
    
    def test_asset_create_date_validation(self):
        """Test asset creation with invalid date range"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(
                category_id=1,
                name="Test Asset",
                purchase_date=date(2024, 12, 31),
                warranty_expiry=date(2024, 1, 1)  # Before purchase date
            )
        assert "Purchase date cannot be after warranty expiry date" in str(exc_info.value)
    
    def test_asset_create_valid_dates(self):
        """Test asset creation with valid date range"""
        data = {
            "category_id": 1,
            "name": "Test Asset",
            "purchase_date": "2024-01-01",
            "warranty_expiry": "2027-01-01"
        }
        schema = AssetCreate(**data)
        assert schema.purchase_date == date(2024, 1, 1)
        assert schema.warranty_expiry == date(2027, 1, 1)
    
    def test_category_create_valid(self):
        """Test valid category creation schema"""
        data = {
            "name": "Laptops",
            "description": "Portable computers"
        }
        schema = CategoryCreate(**data)
        assert schema.name == "Laptops"
        assert schema.description == "Portable computers"
    
    def test_category_create_name_too_short(self):
        """Test category creation with name too short"""
        with pytest.raises(ValidationError):
            CategoryCreate(name="A")  # Less than min_length=2
    
    def test_asset_update_invalid_date_range(self):
        """Test asset update with invalid date range (purchase_date after warranty_expiry)"""
        with pytest.raises(ValidationError) as exc_info:
            AssetUpdate(
                purchase_date=date(2024, 12, 31),
                warranty_expiry=date(2024, 1, 1)  # Before purchase date
            )
        # Should raise validation error for invalid date range
        assert "Purchase date cannot be after warranty expiry date" in str(exc_info.value) or "warranty" in str(exc_info.value).lower()
    
    def test_asset_create_missing_required_fields(self):
        """Test asset creation with missing required fields"""
        # Missing category_id and name (required fields)
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(tag_code="TST-001")
        # Should raise validation error for missing required fields
        assert "category_id" in str(exc_info.value).lower() or "name" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()

