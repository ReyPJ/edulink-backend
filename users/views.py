from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from .models import CustomUser, ClassGrupo, ParentStudentRelation
from .permissions import IsAdmin, IsParent, IsProfesor
from .serializers import (
    UserSerializer,
    ClassGrupoSerializer,
    ParentStundentRelationSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username_or_code = request.data.get("username")
        password = request.data.get("password")

        # Validar si el campo "username" está presente
        if not username_or_code:
            raise ValidationError({"username": "Must include username."})

        # Buscar el usuario por código único o teléfono
        user = CustomUser.objects.filter(
            models.Q(unique_code=username_or_code) | models.Q(phone=username_or_code)
        ).first()

        if not user:
            raise ValidationError({"non_field_errors": ["Invalid credentials."]})

        # Validar si el usuario tiene una contraseña configurada
        if not user.password:
            raise ValidationError(
                {"non_field_errors": ["First time login. Please set your password"]}
            )

        # Verificar la contraseña proporcionada
        if password and user.check_password(password):
            # Si la contraseña es válida, obtenemos los tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )

        # Si las credenciales son incorrectas, lanzar un error
        raise ValidationError(
            {"non_field_errors": ["Invalid credentials. Please try again."]}
        )


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in [CustomUser.ADMIN, CustomUser.PROFESOR]:
            raise PermissionDenied("You do not have permission to create users.")

        serializer.save(center=user.center)
        return Response({"status": "User Created"}, status=status.HTTP_201_CREATED)


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor]

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        if "password" in request.data and request.data["password"]:
            password = request.data["password"]
            request.data["password"] = password

        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role != CustomUser.ADMIN:
            raise PermissionDenied("Only the admin can delete users.")

        if instance.role == CustomUser.ADMIN:
            raise PermissionDenied("You cannot delete an Admin user.")

        instance.delete()


class ClassListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassGrupoSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor]

    def get_queryset(self):
        user = self.request.user

        if user.role == CustomUser.ADMIN:
            return ClassGrupo.objects.filter(center=user.center)
        elif user.role == CustomUser.PROFESOR:
            return ClassGrupo.objects.filter(center=user.center)
        elif user.role == CustomUser.STUDENT:
            return ClassGrupo.objects.filter(students=user)
        elif user.role == CustomUser.FATHER:
            return ClassGrupo.objects.filter(students__parents=user)

        return ClassGrupo.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in [CustomUser.ADMIN, CustomUser.PROFESOR]:
            raise PermissionDenied("You do not have permission to create classes.")

        serializer.save(center=user.center)


class ParentStudentRelationView(generics.ListCreateAPIView):
    queryset = ParentStudentRelation.objects.all()
    serializer_class = ParentStundentRelationSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsParent]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != CustomUser.FATHER and user.role != CustomUser.ADMIN:
            raise PermissionDenied(
                "You do not have permission to create this relation."
            )

        serializer.save()
