import os
import importlib.util
from fastapi.testclient import TestClient


# Load the app module directly from src/app.py so tests work regardless of package layout
repo_root = os.path.dirname(os.path.dirname(__file__))
app_path = os.path.join(repo_root, "src", "app.py")
spec = importlib.util.spec_from_file_location("app_module", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = getattr(app_module, "app")

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Check a few expected activity names exist
    for key in ["Chess Club", "Programming Class"]:
        assert key in data


def test_signup_and_unregister_flow():
    # Choose an activity and create a unique test email
    activity = "Chess Club"
    test_email = "pytest-user@example.test"

    # Ensure the test email is not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if test_email in participants:
        # remove if it exists to start clean
        client.delete(f"/activities/{activity}/participants?email={test_email}")

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    assert test_email in client.get("/activities").json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={test_email}")
    assert resp.status_code == 200
    assert test_email not in client.get("/activities").json()[activity]["participants"]
