from fastapi.testclient import TestClient
from app.main import create_app

client = TestClient(create_app())

def test_draft_connect_exact_text():
    payload = {
        "first_name": "Peter",
        "role_title": "Country Manager",
        "location": "Davao",
        "work_mode": "hybrid",
    }
    r = client.post("/outreach/draft/connect", json=payload)
    assert r.status_code == 200
    text = r.json()["text"]

    # This must exactly match your stored template with variables filled.
    expected = (
        "Hi Peter, I'm Jean from Bershaw. I'm recruiting for our client, "
        "a globally influential technology innovator transforming the insurance industry. "
        "They're hiring a Country Manager in Davao (hybrid). Are you currently exploring? "
        "If so, can you please send your updated CV?"
    )
    assert text == expected

def test_draft_after_accept_exact_text():
    r = client.post("/outreach/draft/after-accept", json={"first_name": "Peter"})
    assert r.status_code == 200
    text = r.json()["text"]
    expected = (
        "Sure, Peter. Please see the attached JD. I'll wait for your CV. "
        "How much is your current and expected salary? How long is your notice period?"
    )
    assert text == expected

def test_route_reply_positive_reply_triggers_salary_notice_jd():
    payload = {
        "first_name": "Peter",
        "message_text": "Hi Jean thank you for the message, sure Jean kindly share my CV and again thanks indeed",
        "jd_link_available": True
    }
    r = client.post("/outreach/route-reply", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "positive_reply"
    assert body["reply"] == (
        "Sure, Peter. Please see the attached JD. I'll wait for your CV. "
        "How much is your current and expected salary? How long is your notice period?"
    )

def test_route_reply_cv_attached_path():
    payload = {
        "first_name": "Peter",
        "message_text": "Please find my CV attached. Thanks!",
        "jd_link_available": True
    }
    r = client.post("/outreach/route-reply", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "cv_attached"
    assert "confirm your current and expected salary" in body["reply"].lower()
    assert "notice period" in body["reply"].lower()

def test_route_reply_decline_path():
    payload = {
        "first_name": "Peter",
        "message_text": "Thanks, but not interested at the moment.",
        "jd_link_available": True
    }
    r = client.post("/outreach/route-reply", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "decline"
    assert "appreciate the reply" in body["reply"].lower()

def test_route_reply_unknown_fallback():
    payload = {
        "first_name": "Peter",
        "message_text": "👋",
        "jd_link_available": False
    }
    r = client.post("/outreach/route-reply", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "unknown"
    # Fallback should still request CV + salary + notice in your tone
    assert "share your updated cv" in body["reply"].lower()
    assert "salary" in body["reply"].lower()
    assert "notice period" in body["reply"].lower()
