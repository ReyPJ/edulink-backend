from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsParent, IsProfesor, IsStudent, IsAdmin
from .models import NoteBook, NoteBookPages
from rest_framework.response import Response
from .serializers import NoteBookPagesSerializer, NoteBookSerializer
from users.models import CustomUser


class NoteBookListCreateView(generics.ListCreateAPIView):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor | IsParent | IsStudent]

    # Modificar la respuesta para que el campo student no muestre solo el id, sino el nombre completo
    # Primero hay que buscar el id en el campo users.models.CustomUser
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = NoteBookSerializer(queryset, many=True)
        for data in serializer.data:
            student_id = data['student']
            student = CustomUser.objects.get(id=student_id)
            data['student'] = student.get_full_name()
        return Response(serializer.data)


class NoteBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer
    permission_classes = [IsAuthenticated, IsProfesor, IsParent, IsStudent]


class NoteBookPagesListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteBookPagesSerializer
    permission_classes = [IsAuthenticated, IsProfesor | IsParent | IsStudent | IsAdmin]

    def get_queryset(self):
        notebook_id = self.kwargs.get('notebook_id')
        return NoteBookPages.objects.filter(notebook_id=notebook_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data_list = serializer.data
        for data in data_list:
            if data['student']:
                try:
                    student = CustomUser.objects.get(id=data['student'])
                    data['student'] = f"{student.first_name} {student.last_name}"
                except CustomUser.DoesNotExist:
                    data['student'] = None
        return Response(data_list)


class NoteBookPagesDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteBookPages.objects.all()
    serializer_class = NoteBookPagesSerializer
    permission_classes = [IsAuthenticated, IsProfesor, IsParent, IsStudent]
