import pytest
from rest_framework.test import APIClient
from users.models import CustomUser, ClassGrupo
from rest_framework.exceptions import PermissionDenied


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return CustomUser.objects.create(
        username="admin_user",
        password="adminpass",
        role=CustomUser.ADMIN,
        center="Test Center1",
        unique_code="admin1",
    )


@pytest.fixture
def profesor_user():
    return CustomUser.objects.create(
        username="profesor_user",
        password="profesorpass",
        role=CustomUser.PROFESOR,
        center="Test Center1",
        unique_code="profesor1",
    )


@pytest.fixture
def student_user():
    return CustomUser.objects.create(
        username="student_user",
        password="studentpass",
        role=CustomUser.STUDENT,
        center="Test Center1",
        unique_code="student1",
    )


@pytest.fixture
def parent_user():
    return CustomUser.objects.create(
        username="parent_user",
        password="parentpass",
        role=CustomUser.FATHER,
        center="Test Center1",
        unique_code="parent1",
    )


@pytest.fixture
def class_group(admin_user, profesor_user):
    """Crea una clase para pruebas"""
    class_group = ClassGrupo.objects.create(
        name="math 101",
        teacher=profesor_user,
        center="Test Center1",
    )
    class_group.students.add(admin_user)
    return class_group


@pytest.mark.django_db
class TestClassListCreateView:

    def test_admin_can_see_only_their_center_classes(
        self, api_client, admin_user, class_group
    ):
        api_client.login(username=admin_user.unique_code, password="adminpass")
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/classes/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "math 101"
