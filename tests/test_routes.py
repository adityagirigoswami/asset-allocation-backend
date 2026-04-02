"""Basic tests for API routes"""
import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient


def make_user(id="11111111-1111-1111-1111-111111111111", email="user@example.com", role_name="employee"):
    return SimpleNamespace(
        id=id,
        email=email,
        password_hash="hashed",
        full_name="Test User",
        role=SimpleNamespace(name=role_name)
    )


def make_role(id=2, name="employee"):
    return SimpleNamespace(id=id, name=name)


def make_asset(id="aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa", name="Laptop", status="available", tag_code="LAP-001"):
    return SimpleNamespace(
        id=id,
        name=name,
        status=status,
        tag_code=tag_code,
        serial_number=None,
        deleted_at=None
    )


def make_allocation(id="alloc-1111", employee_id="u-1111", returned_at=None):
    return SimpleNamespace(
        id=id,
        employee_id=employee_id,
        returned_at=returned_at,
        deleted_at=None
    )


# ========== AUTH ROUTES ==========
class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_login_invalid_credentials(self, client, fake_session_factory, override_dependencies):
        """Test login with invalid credentials"""
        fs = fake_session_factory({"User": []})
        override_dependencies.set_db(fs)
        
        res = client.post("/auth/login", json={"email": "x@x.com", "password": "pw"})
        assert res.status_code == 401
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False
    
    def test_login_success(self, monkeypatch, client, fake_session_factory, override_dependencies):
        """Test successful login"""
        user = make_user()
        fs = fake_session_factory({"User": [user]})
        override_dependencies.set_db(fs)
        
        # Mock password verification and token creation
        import api.routes.auth_routes as auth_routes
        monkeypatch.setattr(auth_routes, "verify_password", lambda a, b: True)
        monkeypatch.setattr(auth_routes, "create_access_token", lambda sub: "access_token")
        monkeypatch.setattr(auth_routes, "create_refresh_token", lambda sub: "refresh_token")
        
        res = client.post("/auth/login", json={"email": user.email, "password": "pw"})
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert "refresh_token" in res.json()
    
    def test_password_reset_request(self, monkeypatch, client, fake_session_factory, override_dependencies):
        """Test password reset request"""
        user = make_user()
        fs = fake_session_factory({"User": [user]})
        override_dependencies.set_db(fs)
        
        async def mock_send_email(*args, **kwargs):
            return None
        
        monkeypatch.setattr("api.routes.auth_routes.EmailService.create_reset_html", lambda **k: "html")
        monkeypatch.setattr("api.routes.auth_routes.EmailService.send_email", mock_send_email)
        
        res = client.post("/auth/password/reset-request", json={"email": user.email})
        assert res.status_code == 200
        # Password reset returns success message in "detail" key (not an error)
        assert "reset link" in res.json().get("detail", "").lower() or "email" in res.json().get("detail", "").lower()


# ========== ASSET ROUTES ==========
class TestAssetRoutes:
    """Test asset endpoints"""
    
    def test_delete_asset_assigned(self, client, fake_session_factory, override_dependencies):
        """Test deleting an assigned asset (should fail)"""
        assigned = make_asset(status="assigned")
        fs = fake_session_factory({"Asset": [assigned]})
        override_dependencies.set_db(fs)
        override_dependencies.set_require_admin(make_user(role_name="admin"))
        
        res = client.delete(f"/assets/{assigned.id}")
        assert res.status_code == 400
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False
        assert "assigned" in res.json()["error"].lower()
    
    def test_create_asset_unauthorized(self, client, fake_session_factory, override_dependencies):
        """Test creating asset without admin authentication (should fail)"""
        fs = fake_session_factory({"Category": [], "Asset": []})
        override_dependencies.set_db(fs)
        # No admin authentication override set
        
        res = client.post("/assets", json={
            "category_id": 1,
            "name": "Test Asset",
            "tag_code": "TST-001"
        })
        assert res.status_code == 401
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False
    
    def test_create_asset_invalid_data(self, client, fake_session_factory, override_dependencies):
        """Test creating asset with invalid/missing required fields"""
        fs = fake_session_factory({"Category": [], "Asset": []})
        override_dependencies.set_db(fs)
        # set_require_admin now automatically overrides both require_admin and get_current_user
        override_dependencies.set_require_admin(make_user(role_name="admin"))
        
        # Missing required field (name)
        res = client.post("/assets", json={
            "category_id": 1,
            "tag_code": "TST-001"
        })
        assert res.status_code == 422
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False


# ========== ALLOCATION ROUTES ==========
class TestAllocationRoutes:
    """Test allocation endpoints"""
    
    def test_create_allocation_unauthorized(self, client, fake_session_factory, override_dependencies):
        """Test creating allocation without authentication (should fail)"""
        fs = fake_session_factory({"Asset": [], "Allocation": []})
        override_dependencies.set_db(fs)
        # No authentication override set
        
        res = client.post("/allocations", json={"asset_id": "test-id", "employee_id": "emp-id"})
        assert res.status_code == 401
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False
    
    def test_create_allocation_invalid_data(self, client, fake_session_factory, override_dependencies):
        """Test creating allocation with invalid/missing required fields"""
        fs = fake_session_factory({"Asset": [], "Allocation": []})
        override_dependencies.set_db(fs)
        # set_require_admin now automatically overrides both require_admin and get_current_user
        override_dependencies.set_require_admin(make_user(role_name="admin"))
        
        # Missing required fields (asset_id, employee_id)
        res = client.post("/allocations", json={})
        assert res.status_code == 422
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False


# ========== RETURN REQUEST ROUTES ==========
class TestReturnRequestRoutes:
    """Test return request endpoints"""
    
    def test_create_return_request_not_found(self, client, fake_session_factory, override_dependencies):
        """Test creating return request for non-existent allocation"""
        fs = fake_session_factory({"Allocation": []})
        override_dependencies.set_db(fs)
        override_dependencies.set_current_user(make_user())
        
        res = client.post("/requests", json={"allocation_id": "missing", "description": "x"})
        assert res.status_code == 404
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False
    
    def test_create_return_request_wrong_employee(self, client, fake_session_factory, override_dependencies):
        """Test creating return request for another employee's allocation"""
        alloc = make_allocation(employee_id="other-employee")
        fs = fake_session_factory({"Allocation": [alloc]})
        override_dependencies.set_db(fs)
        override_dependencies.set_current_user(make_user(id="current-user"))
        
        res = client.post("/requests", json={"allocation_id": alloc.id, "description": "x"})
        assert res.status_code == 403
        # Verify standardized error response format
        assert "error" in res.json()
        assert "status_code" in res.json()
        assert res.json()["success"] == False
    

