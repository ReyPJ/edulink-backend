from django.urls import path
from .views import (NoteBookListCreateView, NoteBookDetailView, NoteBookPagesListCreateView, NoteBookPagesDetailView)


urlpatterns = [
    path('notebooks/', NoteBookListCreateView.as_view(), name='notebook_list_create'),
    path('notebooks/<int:pk>/', NoteBookDetailView.as_view(), name='notebook_detail'),
    path('notebooks/<int:notebook_id>/pages/', NoteBookPagesListCreateView.as_view(), name='notebook_pages_list_create'),
    path('notebooks/pages/<int:pk>/', NoteBookPagesDetailView.as_view(), name='notebook_pages_detail'),
]
