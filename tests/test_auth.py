import pytest

from app import create_app, db
from app.models import User


@pytest.fixture()
def app():
    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        user = User(username="admin", full_name="Admin")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()


def test_login_success(app):
    client = app.test_client()
    response = client.post("/auth/login", data={"username": "admin", "password": "secret"}, follow_redirects=True)
    assert response.status_code == 200
    assert "لوحة التحكم" in response.get_data(as_text=True)


def test_login_rejects_bad_password(app):
    client = app.test_client()
    response = client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
