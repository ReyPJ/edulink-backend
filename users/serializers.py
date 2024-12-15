from rest_framework import serializers
from .models import CustomUser, ClassGrupo


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

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
            "password": {"write_only": True, "required": False},
            "unique_code": {"required": True},
        }

    def create(self, validated_data):
        role = validated_data.get("role", CustomUser.STUDENT)
        password = validated_data.pop("password", None)

        if role == CustomUser.STUDENT:
            user = CustomUser.objects.create(**validated_data)

        else:
            if not password:
                raise serializers.ValidationError(
                    {"password": "Password is required for non-student roles."}
                )

            user = CustomUser.objects.create(**validated_data)
            user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ClassGrupoSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.PROFESOR)
    )
    students = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.STUDENT), many=True
    )

    teacher_name = serializers.SerializerMethodField()
    students_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassGrupo
        fields = "__all__"

    def get_students_name(self, obj):
        return [student.get_full_name() for student in obj.students.all()]

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else None