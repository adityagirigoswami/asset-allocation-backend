import pytest
from types import SimpleNamespace


def make_asset(id="aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa", name="Laptop", status="available", tag_code=None, serial_number=None):
    return SimpleNamespace(id=id, name=name, status=status, tag_code=tag_code, serial_number=serial_number)


def test_create_asset_duplicate_tag(client, fake_session_factory, override_dependencies):
    existing = make_asset(tag_code="T1")
    fs = fake_session_factory({"Asset": [existing]})
    override_dependencies.set_db(fs)

    payload = {"name": "New", "tag_code": "T1"}
    res = client.post("/assets", json=payload)
    assert res.status_code == 409


def test_create_asset_success(monkeypatch, client, fake_session_factory, override_dependencies):
    fs = fake_session_factory({"Asset": []})
    override_dependencies.set_db(fs)

    # creation should succeed
    payload = {"name": "NewAsset"}
    res = client.post("/assets", json=payload)
    assert res.status_code == 200
    assert res.json()["name"] == "NewAsset"


def test_delete_asset_assigned(client, fake_session_factory, override_dependencies):
    assigned = make_asset(status="assigned")
    fs = fake_session_factory({"Asset": [assigned]})
    override_dependencies.set_db(fs)

    res = client.delete(f"/assets/{assigned.id}")
    assert res.status_code == 400
