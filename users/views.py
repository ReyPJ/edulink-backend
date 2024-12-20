from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from .models import CustomUser, ClassGrupo, ParentChild
from .permissions import IsAdmin, IsParent, IsProfesor, IsStudent
from .serializers import (
    UserSerializer,
    ClassGrupoSerializer,
    ParentChildSerializer,
    ParentChildListSerializer,
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
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in [CustomUser.ADMIN, CustomUser.PROFESOR]:
            raise PermissionDenied("You do not have permission to create users.")

        serializer.save(center=user.center)
        return Response({"status": "User Created"}, status=status.HTTP_201_CREATED)

    # get_queryset to return only users from the same center
    def get_queryset(self):
        user = self.request.user

        if user.role == CustomUser.ADMIN:
            return CustomUser.objects.filter(center=user.center)
        elif user.role == CustomUser.PROFESOR:
            return CustomUser.objects.filter(center=user.center)

        return CustomUser.objects.all()


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor | IsParent | IsStudent]

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


class ParentChildCreateView(generics.CreateAPIView):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor]


class ParentClassListView(generics.ListAPIView):
    serializer_class = ClassGrupoSerializer
    permission_classes = [IsAuthenticated, IsParent | IsProfesor | IsAdmin | IsStudent]

    def get_queryset(self):
        user = self.request.user
        if user.role == CustomUser.FATHER:
            children = ParentChild.objects.filter(parent=user).values_list("child")
            return ClassGrupo.objects.filter(students__in=children).distinct()
        elif user.role == CustomUser.STUDENT:
            return ClassGrupo.objects.filter(students=user).distinct()

        raise PermissionDenied("You do not have permission to view this class.")


class ParentChildListView(generics.ListAPIView):
    serializer_class = ParentChildListSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProfesor]

    def get_queryset(self):
        user = self.request.user
        if user.role in [CustomUser.ADMIN, CustomUser.PROFESOR]:
            return ParentChild.objects.filter(
                parent__center=user.center
            ).select_related('parent', 'child')
        raise PermissionDenied("You do not have permission to view this list.")
