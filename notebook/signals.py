from django.db.models import signals
from django.dispatch import receiver
from users.models import CustomUser
from .models import NoteBook


@receiver(signals.post_save, sender=CustomUser)
def create_notebook_for_student(sender, instance, created, **kwargs):
    if created and instance.role == CustomUser.STUDENT: 
        NoteBook.objects.create(student=instance)
