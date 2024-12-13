import pytest
from rest_framework.test import APIClient
from users.models import CustomUser

TOKEN_URL = "/api/token/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCustomTokenObtainPair:

    def test_missing_username(self, api_client):
        """Caso 1: No se proporciona usarname ni unique_code."""
        data = {"password": "testpassword"}
        response = api_client.post(TOKEN_URL, data)
        assert response.status_code == 400
        assert response.data["username"] == "Must include username."

    def test_user_not_found(self, api_client):
        """Caso 2: El usuario no existe."""
        data = {"username": "nonexist_user", "password": "testpassword"}
        response = api_client.post(TOKEN_URL, data)
        assert response.status_code == 400
        assert "Invalid credentials." in [
            str(error) for error in response.data["non_field_errors"]
        ]

    def test_first_time_login(self, api_client):
        """Caso 3: Primer inicio de sesion sin password configurada"""
        CustomUser.objects.create(
            username="", unique_code="U123", phone="", password=""
        )
        data = {"username": "U123"}
        response = api_client.post(TOKEN_URL, data)
        assert response.status_code == 400
        assert "First time login. Please set your password" in [
            str(error) for error in response.data["non_field_errors"]
        ]

    def test_invalid_password(self, api_client):
        """Caso 4: Password Incorrecta"""
        CustomUser.objects.create(
            username="testuser",
            unique_code="U123",
            phone="123456",
            password="correctpassword",
        )
        data = {"username": "123456", "password": "wrongpassword"}
        response = api_client.post(TOKEN_URL, data)
        assert response.status_code == 400
        assert "Invalid credentials. Please try again." in [
            str(error) for error in response.data["non_field_errors"]
        ]

    @pytest.mark.parametrize("username_field", ["unique_code", "phone"])
    def test_successful_login(self, api_client, username_field):
        """Caso 5-6: Inicio de sesion exitoso usando, unique code o phone"""
        user = CustomUser.objects.create(
            username="testuser",
            unique_code="U123",
            phone="123456789",
        )
        user.set_password("correctpass")
        user.save()

        username_value = {
            "unique_code": user.unique_code,
            "phone": user.phone,
        }[username_field]

        data = {"username": username_value, "password": "correctpass"}
        response = api_client.post(TOKEN_URL, data)

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
