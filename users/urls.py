from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailUpdateDeleteView,
    ClassListCreateView,
    ParentStudentRelationView,
)

urlpatterns = [
    # Usuarios
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path(
        "users/<int:pk>/",
        UserDetailUpdateDeleteView.as_view(),
        name="user-detail-delete-update",
    ),
    # Clases
    path("classes/", ClassListCreateView.as_view(), name="class-list-create"),
    # Relaciones Padre-Estudiante
    path(
        "parent-student-relation",
        ParentStudentRelationView.as_view(),
        name="parent-student-relation",
    ),
]
