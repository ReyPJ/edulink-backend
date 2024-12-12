from rest_framework import serializers
from .models import CustomUser, ClassGrupo, ParentStudentRelation
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "center",
            "unique_code",
            "date_joined",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "unique_code": {"required": True},
        }

        def validate(self, data):
            if CustomUser.objects.filter(email=data["email"]).exists():
                raise serializers.ValidationError(
                    {"email": "This email is alrady in use"}
                )

            if CustomUser.objects.filter(unique_code=data["unique_code"]).exists():
                raise serializers.ValidationError(
                    {"unique_code": "This unique code is already in use"}
                )

            return data

        def create(self, validated_data):
            password = validated_data.pop("password")
            user = CustomUser.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            return user


class ClassGrupoSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.PROFESOR)
    )
    students = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.STUDENT)
    )

    class Meta:
        model = ClassGrupo
        fields = "__all__"


class ParenStundentRelationSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.FATHER)
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.STUDENT)
    )

    class Meta:
        model = ParentStudentRelation
        fields = "__all__"


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_code = attrs.get("username")
        password = attrs.get("password")

        if not username_or_code or not password:
            raise serializers.ValidationError("Must include username and password.")

        user = CustomUser.objects.filter(
            models.Q(unique_code=username_or_code) | models.Q(phone=username_or_code)
        ).first()

        if user and user.check_password(password):
            data = super().validate({"username": user.username, "password": password})
            return data

        raise serializers.ValidationError("Invalid credentials. Please try again.")
