from rest_framework import serializers
from .models import CustomUser, ClassGrupo, ParentChild


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
        password = validated_data.pop("password", None)

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

    def get_students_name(self, obj) -> list[str]:
        return [student.get_full_name() for student in obj.students.all()]

    def get_teacher_name(self, obj) -> str:
        return obj.teacher.get_full_name() if obj.teacher else None


class ParentChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChild
        fields = "__all__"

    def validate(self, data):
        if data["parent"].role != CustomUser.FATHER:
            raise serializers.ValidationError("Only fathers can be parents.")
        if data["child"].role != CustomUser.STUDENT:
            raise serializers.ValidationError("Only students can be children.")
        if ParentChild.objects.filter(parent=data["parent"], child=data["child"]).exists():
            raise serializers.ValidationError("This parent-child relationship already exists.")
        return data


class ParentChildListSerializer(serializers.ModelSerializer):
    parent_detail = UserSerializer(source="parent", read_only=True)
    child_detail = UserSerializer(source="child", read_only=True)

    class Meta:
        model = ParentChild
        fields = ["id", "parent", "child", "parent_detail", "child_detail"]
