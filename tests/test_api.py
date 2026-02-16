import sys
import pathlib
import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from app import app, activities

client = TestClient(app)

def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data

def test_signup_and_unregister_flow():
    activity = "Tennis"
    email = "testuser@example.com"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should fail
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]

def test_nonexistent_activity_errors():
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404
    resp = client.delete("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404
