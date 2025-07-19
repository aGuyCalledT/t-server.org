from django.db import models
import uuid
from datetime import datetime

class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.CharField(max_length=4, blank=True, null=True)
    likes = models.IntegerField(default=0)
    added_date = models.CharField(max_length=50)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.added_date = datetime.now().strftime("%a. %d.%m.%Y")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.year if self.year else 'N/A'})"

    class Meta:
        ordering = ['-added_date']


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField() # TextField für längere Nachrichten
    timestamp = models.DateTimeField(auto_now_add=True) # Speichert das Erstellungsdatum und die Uhrzeit automatisch

    def __str__(self):
        return f"Message from {self.name} <{self.email}> on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        # Sortiere Nachrichten standardmäßig nach dem neuesten Datum
        ordering = ['-timestamp']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
