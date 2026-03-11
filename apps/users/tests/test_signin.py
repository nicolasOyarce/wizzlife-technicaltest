"""
Tests para el endpoint POST /signin/
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

SIGNIN_URL = "/signin/"


@pytest.mark.django_db
class TestSignIn:
    """Tests del endpoint de inicio de sesión."""

    def test_signin_success_returns_200(self, api_client, user):
        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "TestPassword123!"},
            format="json",
        )
        assert response.status_code == 200

    def test_signin_returns_access_token(self, api_client, user):
        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "TestPassword123!"},
            format="json",
        )
        assert "access" in response.data

    def test_signin_returns_refresh_token(self, api_client, user):
        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "TestPassword123!"},
            format="json",
        )
        assert "refresh" in response.data

    def test_signin_returns_user_data(self, api_client, user):
        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "TestPassword123!"},
            format="json",
        )
        assert "user" in response.data
        assert response.data["user"]["email"] == user.email

    def test_signin_wrong_password_returns_401(self, api_client, user):
        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "WrongPassword!"},
            format="json",
        )
        assert response.status_code == 401

    def test_signin_nonexistent_email_returns_401(self, api_client):
        response = api_client.post(
            SIGNIN_URL,
            {"email": "noone@test.com", "password": "AnyPass123!"},
            format="json",
        )
        assert response.status_code == 401

    def test_signin_missing_email_returns_400(self, api_client):
        response = api_client.post(
            SIGNIN_URL,
            {"password": "AnyPass123!"},
            format="json",
        )
        assert response.status_code == 400

    def test_signin_inactive_user_returns_401(self, api_client, user):
        user.is_active = False
        user.save()
        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "TestPassword123!"},
            format="json",
        )
        assert response.status_code == 401

    def test_user_me_returns_profile(self, auth_client, user):
        response = auth_client.get("/users/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_user_me_requires_auth(self, api_client):
        response = api_client.get("/users/me/")
        assert response.status_code == 401
