from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser


class NoteBook(models.Model):
    student = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notebook')

    def clean(self):
        if self.student.role != CustomUser.STUDENT:
            raise ValidationError("Notebook can only be created for students.")


class NoteBookPages(models.Model):
    notebook = models.ForeignKey(NoteBook, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notebook_pages")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notebook_pages_updated", blank=True, null=True)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notebook_pages_to")

    def __str__(self):
        return f"{self.title} - {self.student.username}"
