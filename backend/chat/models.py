from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.participants.count() > 2:
            raise ValidationError('There should be no more than 2 participants')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_participants_str(self) -> str:
        return ', '.join([str(p) for p in self.participants.all()])

    def __str__(self):
        return f"Thread between {self.get_participants_str()}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(verbose_name='Text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} in {self.thread}"
