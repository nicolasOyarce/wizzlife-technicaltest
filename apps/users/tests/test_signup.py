"""
Tests para el endpoint POST /signup/
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

SIGNUP_URL = "/signup/"

VALID_PAYLOAD = {
    "email": "newuser@test.com",
    "username": "newuser",
    "first_name": "New",
    "last_name": "User",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
}


@pytest.mark.django_db
class TestSignUp:
    """Tests del endpoint de registro."""

    def test_signup_success_returns_201(self, api_client):
        response = api_client.post(SIGNUP_URL, VALID_PAYLOAD, format="json")
        assert response.status_code == 201

    def test_signup_creates_user_in_db(self, api_client):
        api_client.post(SIGNUP_URL, VALID_PAYLOAD, format="json")
        assert User.objects.filter(email=VALID_PAYLOAD["email"]).exists()

    def test_signup_returns_jwt_tokens(self, api_client):
        response = api_client.post(SIGNUP_URL, VALID_PAYLOAD, format="json")
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]

    def test_signup_returns_user_data(self, api_client):
        response = api_client.post(SIGNUP_URL, VALID_PAYLOAD, format="json")
        assert response.data["email"] == VALID_PAYLOAD["email"]
        assert response.data["username"] == VALID_PAYLOAD["username"]

    def test_signup_email_normalized_to_lowercase(self, api_client):
        payload = {**VALID_PAYLOAD, "email": "UPPER@TEST.COM", "username": "upperuser"}
        api_client.post(SIGNUP_URL, payload, format="json")
        assert User.objects.filter(email="upper@test.com").exists()

    def test_signup_password_not_in_response(self, api_client):
        response = api_client.post(SIGNUP_URL, VALID_PAYLOAD, format="json")
        assert "password" not in response.data
        assert "password_confirm" not in response.data

    def test_signup_duplicate_email_returns_400(self, api_client, user):
        payload = {**VALID_PAYLOAD, "email": user.email, "username": "uniqueuser999"}
        response = api_client.post(SIGNUP_URL, payload, format="json")
        assert response.status_code == 400

    def test_signup_duplicate_username_returns_400(self, api_client, user):
        payload = {**VALID_PAYLOAD, "username": user.username}
        response = api_client.post(SIGNUP_URL, payload, format="json")
        assert response.status_code == 400

    def test_signup_password_mismatch_returns_400(self, api_client):
        payload = {**VALID_PAYLOAD, "password_confirm": "DifferentPass456!"}
        response = api_client.post(SIGNUP_URL, payload, format="json")
        assert response.status_code == 400

    def test_signup_weak_password_returns_400(self, api_client):
        payload = {**VALID_PAYLOAD, "username": "uniqueuser2", "email": "unique2@test.com", "password": "123", "password_confirm": "123"}
        response = api_client.post(SIGNUP_URL, payload, format="json")
        assert response.status_code == 400

    def test_signup_missing_email_returns_400(self, api_client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "email"}
        response = api_client.post(SIGNUP_URL, payload, format="json")
        assert response.status_code == 400

    def test_signup_missing_password_returns_400(self, api_client):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "password"}
        response = api_client.post(SIGNUP_URL, payload, format="json")
        assert response.status_code == 400
