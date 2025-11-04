from fastapi.testclient import TestClient
from app.main import create_app

client = TestClient(create_app())

def test_default_tone_templates_snapshot():
    r = client.get("/tone/profile")
    assert r.status_code == 200
    tp = r.json()
    assert tp["persona_name"] == "Jean from Bershaw"
    assert "initial_connect" in tp["templates"]
    assert "after_accept_send_jd" in tp["templates"]
