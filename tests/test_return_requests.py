import pytest
from types import SimpleNamespace


def make_alloc(id="alloc-1111", employee_id="u-1111", returned_at=None):
    return SimpleNamespace(id=id, employee_id=employee_id, returned_at=returned_at)


def make_user(id="u-1111"):
    return SimpleNamespace(id=id)


def test_create_return_request_alloc_not_found(client, fake_session_factory, override_dependencies):
    fs = fake_session_factory({"Allocation": []})
    override_dependencies.set_db(fs)
    override_dependencies.set_current_user(make_user())

    res = client.post("/return-requests", json={"allocation_id": "missing", "description": "x"})
    assert res.status_code == 404


def test_create_return_request_mismatch_employee(client, fake_session_factory, override_dependencies):
    alloc = make_alloc(employee_id="other")
    fs = fake_session_factory({"Allocation": [alloc]})
    override_dependencies.set_db(fs)
    override_dependencies.set_current_user(make_user(id="u-1111"))

    res = client.post("/return-requests", json={"allocation_id": alloc.id, "description": "x"})
    assert res.status_code == 403


def test_create_return_request_success(client, fake_session_factory, override_dependencies):
    alloc = make_alloc(employee_id="u-1111", returned_at=None)
    fs = fake_session_factory({"Allocation": [alloc]})
    override_dependencies.set_db(fs)
    override_dependencies.set_current_user(make_user(id="u-1111"))

    res = client.post("/return-requests", json={"allocation_id": alloc.id, "description": "please"})
    assert res.status_code == 200
