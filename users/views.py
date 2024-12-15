from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from .models import CustomUser, ClassGrupo
from .permissions import IsAdmin, IsParent, IsProfesor, IsStudent
from .serializers import (
    UserSerializer,
    ClassGrupoSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username_or_code = request.data.get("username")
        password = request.data.get("password")

        if not username_or_code:
            raise ValidationError({"username": "Must include username."})

        user = CustomUser.objects.filter(
            models.Q(unique_code=username_or_code) | models.Q(phone=username_or_code)
        ).first()

        if not user:
            raise ValidationError({"non_field_errors": ["Invalid credentials."]})

        if not user.password:
            raise ValidationError(
                {"non_field_errors": ["First time login. Please set your password"]}
            )

        if password and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )

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
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor | IsParent | IsStudent]

    def get_queryset(self):
        user = self.request.user

        if user.role == CustomUser.ADMIN:
            return ClassGrupo.objects.filter(center=user.center)
        elif user.role == CustomUser.PROFESOR:
            return ClassGrupo.objects.filter(center=user.center)
        elif user.role == CustomUser.STUDENT:
            return ClassGrupo.objects.filter(students=user)

        return ClassGrupo.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in [CustomUser.ADMIN, CustomUser.PROFESOR]:
            raise PermissionDenied("You do not have permission to create classes.")

        serializer.save(center=user.center)
