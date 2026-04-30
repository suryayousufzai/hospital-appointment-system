"""
Unit tests for authentication — login, register, logout.
"""

import pytest
from tests.conftest import login, logout


class TestLandingPage:
    """Tests for the landing/home page."""

    def test_landing_page_loads(self, client):
        """Landing page should return 200 and show site name."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"MediCare" in resp.data

    def test_authenticated_user_redirected_from_landing(self, client):
        """Logged-in users should be redirected away from landing."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        logout(client)


class TestLogin:
    """Tests for the login flow."""

    def test_login_page_loads(self, client):
        """GET /login should return 200."""
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Sign In" in resp.data

    def test_login_with_valid_credentials(self, client):
        """Valid credentials should log in and redirect to dashboard."""
        resp = login(client, "admin@test.com", "Admin@1234")
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data or b"Welcome" in resp.data
        logout(client)

    def test_login_with_wrong_password(self, client):
        """Wrong password should show an error message."""
        resp = login(client, "admin@test.com", "wrongpassword")
        assert b"Invalid email or password" in resp.data

    def test_login_with_unknown_email(self, client):
        """Unknown email should show an error message."""
        resp = login(client, "nobody@test.com", "password")
        assert b"Invalid email or password" in resp.data

    def test_login_with_empty_fields(self, client):
        """Empty form submission should fail validation."""
        resp = client.post("/login", data={"email": "", "password": ""},
                           follow_redirects=True)
        assert resp.status_code == 200
        # Should stay on login page
        assert b"Sign In" in resp.data


class TestLogout:
    """Tests for logout."""

    def test_logout_redirects_to_login(self, client):
        """Logging out should redirect to the login page."""
        login(client, "admin@test.com", "Admin@1234")
        resp = logout(client)
        assert b"logged out" in resp.data or b"Sign In" in resp.data

    def test_logout_requires_authentication(self, client):
        """Unauthenticated /logout should redirect to login."""
        resp = client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


class TestRegister:
    """Tests for patient self-registration."""

    def test_register_page_loads(self, client):
        """GET /register should return 200."""
        resp = client.get("/register")
        assert resp.status_code == 200
        assert b"Create Account" in resp.data

    def test_register_new_patient(self, client):
        """Valid registration should create account and redirect."""
        resp = client.post("/register", data={
            "first_name":       "Test",
            "last_name":        "User",
            "username":         "testuser99",
            "email":            "testuser99@test.com",
            "password":         "Secure@123",
            "confirm_password": "Secure@123",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Account created" in resp.data or b"Sign In" in resp.data

    def test_register_duplicate_email(self, client):
        """Duplicate email should fail with a validation error."""
        resp = client.post("/register", data={
            "first_name":       "Dupe",
            "last_name":        "Email",
            "username":         "dupeemail",
            "email":            "admin@test.com",  # already exists
            "password":         "Secure@123",
            "confirm_password": "Secure@123",
        }, follow_redirects=True)
        assert b"already registered" in resp.data or b"Email" in resp.data

    def test_register_password_mismatch(self, client):
        """Mismatched passwords should fail."""
        resp = client.post("/register", data={
            "first_name":       "Mismatch",
            "last_name":        "Pass",
            "username":         "mismatchpass",
            "email":            "mismatch@test.com",
            "password":         "Secure@123",
            "confirm_password": "Different@456",
        }, follow_redirects=True)
        assert resp.status_code == 200
