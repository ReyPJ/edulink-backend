from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsParent, IsProfesor, IsStudent
from .models import NoteBook, NoteBookPages
from .serializers import NoteBookPagesSerializer, NoteBookSerializer


class NoteBookListCreateView(generics.ListCreateAPIView):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer
    permission_classes = [IsAuthenticated, IsProfesor, IsParent, IsStudent]


class NoteBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer
    permission_classes = [IsAuthenticated, IsProfesor, IsParent, IsStudent]


class NoteBookPagesListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteBookPagesSerializer
    permission_classes = [IsAuthenticated, IsProfesor, IsParent, IsStudent]

    def get_queryset(self):
        notebook_id = self.kwargs.get('notebook_id')
        return NoteBookPages.objects.filter(notebook_id=notebook_id)


class NoteBookPagesDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteBookPages.objects.all()
    serializer_class = NoteBookPagesSerializer
    permission_classes = [IsAuthenticated, IsProfesor, IsParent, IsStudent]
