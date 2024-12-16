from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailUpdateDeleteView,
    ClassListCreateView,
    ParentClassListView,
    ParentChildCreateView,
    ParentChildListView
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
    # Padres e hijos
    path("parent-child/", ParentChildCreateView.as_view(), name="parent-child-create"),
    path("parent-child/classes-list/", ParentClassListView.as_view(), name="parent-class-list"),
    path("parent-child/list/", ParentChildListView.as_view(), name="parent-child-list"),
]
