import pytest
from types import SimpleNamespace


def make_asset(id="aaaaaaaa-2222-2222-2222-aaaaaaaaaaaa", status="available"):
    return SimpleNamespace(id=id, status=status)


def make_user(id="11111111-1111-1111-1111-111111111111"):
    return SimpleNamespace(id=id)


def test_allocate_asset_not_found(client, fake_session_factory, override_dependencies):
    fs = fake_session_factory({"Asset": []})
    override_dependencies.set_db(fs)

    # set current user to an admin-like object for allocated_by
    override_dependencies.set_current_user(make_user())

    payload = {"asset_id": "missing", "employee_id": "111", "allocation_date": "2025-01-01"}
    res = client.post("/allocations", json=payload)
    assert res.status_code == 404


def test_allocate_asset_not_available(client, fake_session_factory, override_dependencies):
    asset = make_asset(status="assigned")
    fs = fake_session_factory({"Asset": [asset]})
    override_dependencies.set_db(fs)
    override_dependencies.set_current_user(make_user())

    payload = {"asset_id": asset.id, "employee_id": "111", "allocation_date": "2025-01-01"}
    res = client.post("/allocations", json=payload)
    assert res.status_code == 409


def test_allocate_asset_success(client, fake_session_factory, override_dependencies):
    asset = make_asset(status="available")
    fs = fake_session_factory({"Asset": [asset]})
    override_dependencies.set_db(fs)
    override_dependencies.set_current_user(make_user())

    payload = {"asset_id": asset.id, "employee_id": "11111111-1111-1111-1111-111111111111", "allocation_date": "2025-01-01"}
    res = client.post("/allocations", json=payload)
    assert res.status_code == 200
