import pytest
from types import SimpleNamespace
from api.utils.jwt_handler import create_access_token, create_refresh_token
import api.routes.auth_routes as auth_routes


def make_user(id="11111111-1111-1111-1111-111111111111", email="u@example.com", role_name="employee"):
    return SimpleNamespace(id=id, email=email, password_hash="hashed", full_name="U Test", role=SimpleNamespace(name=role_name))


def make_role(id=2, name="employee"):
    return SimpleNamespace(id=id, name=name)


def make_password_token(token="tok", user_id="11111111-1111-1111-1111-111111111111", expires_at=None):
    return SimpleNamespace(token=token, user_id=user_id, expires_at=expires_at, used_at=None, deleted_at=None)


def test_login_invalid(client, fake_session_factory, override_dependencies):
    # no users in DB
    fs = fake_session_factory({"User": []})
    override_dependencies.set_db(fs)

    res = client.post("/auth/login", json={"email": "x@x.com", "password": "pw"})
    assert res.status_code == 401


def test_login_success(monkeypatch, client, fake_session_factory, override_dependencies):
    user = make_user()
    fs = fake_session_factory({"User": [user]})
    override_dependencies.set_db(fs)

    # force verify_password to True and tokens deterministic
    monkeypatch.setattr(auth_routes, "verify_password", lambda a, b: True)
    monkeypatch.setattr(auth_routes, "create_access_token", lambda sub: "atoken")
    monkeypatch.setattr(auth_routes, "create_refresh_token", lambda sub: "rtoken")

    res = client.post("/auth/login", json={"email": user.email, "password": "pw"})
    assert res.status_code == 200
    assert res.json()["access_token"] == "atoken"


def test_password_reset_request_no_user(client, fake_session_factory, override_dependencies):
    fs = fake_session_factory({"User": []})
    override_dependencies.set_db(fs)

    res = client.post("/auth/password/reset-request", json={"email": "missing@example.com"})
    assert res.status_code == 200
    assert "reset link" in res.json()["detail"]


def test_password_reset_request_with_user(monkeypatch, client, fake_session_factory, override_dependencies):
    user = make_user()
    fs = fake_session_factory({"User": [user]})
    override_dependencies.set_db(fs)

    # no-op send
    monkeypatch.setattr("api.routes.auth_routes.EmailService.create_reset_html", lambda **k: "html")
    monkeypatch.setattr("api.routes.auth_routes.EmailService.send_email", lambda *a, **k: None)

    res = client.post("/auth/password/reset-request", json={"email": user.email})
    assert res.status_code == 200
    assert "reset link" in res.json()["detail"]


def test_confirm_password_reset_invalid_token(client, fake_session_factory, override_dependencies):
    fs = fake_session_factory({"PasswordResetToken": []})
    override_dependencies.set_db(fs)

    res = client.post("/auth/password/reset", json={"token": "bad", "new_password": "abc123"})
    assert res.status_code == 400


def test_refresh_token_invalid(monkeypatch, client, fake_session_factory, override_dependencies):
    fs = fake_session_factory({"User": []})
    override_dependencies.set_db(fs)
    monkeypatch.setattr(auth_routes, "decode_token", lambda t: None)

    res = client.post("/auth/refresh", headers={"X-Refresh-Token": "x"})
    assert res.status_code == 401


def test_create_employee_admin_path(monkeypatch, client, fake_session_factory, override_dependencies):
    # admin-only: need an 'employee' UserRole present
    role = make_role()
    fs = fake_session_factory({"UserRole": [role], "User": []})
    override_dependencies.set_db(fs)

    admin_user = make_user(role_name="admin")
    override_dependencies.set_require_admin(admin_user)

    monkeypatch.setattr(auth_routes, "hash_password", lambda p: "hpass")

    payload = {"email": "e@example.com", "password": "pw", "full_name": "Emp", "employee_code": "E001", "phone": "123"}
    res = client.post("/auth/employees", json=payload)
    assert res.status_code == 200
