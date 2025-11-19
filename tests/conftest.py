import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient

from main import app

import db.auth as db_auth
import core.security as core_security


class FakeQuery:
    def __init__(self, items):
        # items is a list
        self._items = items or []

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return list(self._items)

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, n):
        return self

    def limit(self, n):
        return self


class FakeSession:
    def __init__(self, mapping: dict[str, list] | None = None):
        # mapping: model_identifier -> list of objects
        self.mapping = mapping or {}

    def query(self, model):
        key = getattr(model, "__name__", str(model))
        return FakeQuery(self.mapping.get(key, []))

    def add(self, obj):
        # no-op for tests
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return None

    def close(self):
        return None


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_session_factory():
    """Return a factory that creates FakeSession instances with given mapping."""

    def _factory(mapping=None):
        return FakeSession(mapping)

    return _factory


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    """Provide helpers to tests and ensure default dependency overrides are cleaned up."""

    overrides = {}

    def set_db(fake_session):
        # override get_db dependency used in routes
        def _get_db_override():
            try:
                yield fake_session
            finally:
                pass

        app.dependency_overrides[db_auth.get_db] = _get_db_override
        overrides['db'] = _get_db_override

    def set_current_user(user_obj):
        app.dependency_overrides[core_security.get_current_user] = lambda: user_obj
        overrides['current_user'] = lambda: user_obj

    def set_require_admin(user_obj):
        app.dependency_overrides[core_security.require_admin] = lambda: user_obj
        overrides['require_admin'] = lambda: user_obj

    monkeypatch.setattr("api.utils.mailer.EmailService.send_email", lambda *a, **k: None)

    yield SimpleNamespace(set_db=set_db, set_current_user=set_current_user, set_require_admin=set_require_admin)

    # teardown
    for k in list(app.dependency_overrides.keys()):
        app.dependency_overrides.pop(k, None)
