from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ADMIN = "admin"
    PROFESOR = "profesor"
    FATHER = "father"
    STUDENT = "student"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (PROFESOR, "Profesor"),
        (FATHER, "Father"),
        (STUDENT, "Student"),
    ]

    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default=STUDENT)
    phone = models.CharField(max_length=12, blank=True, null=True)
    center = models.CharField(max_length=250, default="Test School")
    unique_code = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.username} - {self.role} - {self.center}"


class ClassGrupo(models.Model):
    name = models.CharField(max_length=100, default="Grupo A")
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": CustomUser.PROFESOR},
        related_name="clases",
    )
    students = models.ManyToManyField(
        CustomUser,
        limit_choices_to={"role": CustomUser.STUDENT},
        related_name="clase_student",
    )
    center = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name} - {self.center}"
