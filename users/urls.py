from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailUpdateDeleteView,
    ClassListCreateView,
    ParentClassListView
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
    path("parent-classes/", ParentClassListView.as_view(), name="parent-class-list"),
]
