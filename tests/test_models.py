"""Basic tests for database models"""
import pytest
from datetime import datetime, timezone
import uuid
from api.models.users import User
from api.models.user_roles import UserRole
from api.models.assets import Asset
from api.models.categories import Category
from api.utils.enums import AssetStatus


class TestUserModel:
    """Test User model"""
    
    def test_user_creation(self):
        """Test creating a user instance"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            role_id=1
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role_id == 1


class TestUserRoleModel:
    """Test UserRole model"""
    
    def test_role_creation(self):
        """Test creating a role instance"""
        role = UserRole(
            name="test_role",
            description="Test role description"
        )
        assert role.name == "test_role"
        assert role.description == "Test role description"


class TestCategoryModel:
    """Test Category model"""
    
    def test_category_creation(self):
        """Test creating a category instance"""
        category = Category(
            name="Laptops",
            description="Portable computers"
        )
        assert category.name == "Laptops"
        assert category.description == "Portable computers"


class TestAssetModel:
    """Test Asset model"""
    
    def test_asset_creation(self):
        """Test creating an asset instance"""
        asset = Asset(
            category_id=1,
            name="Test Laptop",
            tag_code="LAP-001",
            status=AssetStatus.available
        )
        assert asset.name == "Test Laptop"
        assert asset.tag_code == "LAP-001"
        assert asset.status == AssetStatus.available

