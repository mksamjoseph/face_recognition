from django.db import models
from django.utils import timezone

class KnownPerson(models.Model):
    name = models.CharField(max_length=100)
    embedding = models.BinaryField()
    photo = models.ImageField(upload_to="known_photos/")
    created_at = models.DateTimeField(default=timezone.now)
    camera_name = models.CharField(max_length=100, default="camera_a")

    def __str__(self):
        return self.name

class UnknownPerson(models.Model):
    name = models.CharField(max_length=100, unique=True)
    embedding = models.BinaryField()
    photo = models.ImageField(upload_to="unknown_photos/")
    created_at = models.DateTimeField(default=timezone.now)
    camera_name = models.CharField(max_length=100, default="camera_a")

    def __str__(self):
        return self.name


class PersonSighting(models.Model):
    known_person = models.ForeignKey(KnownPerson, on_delete=models.CASCADE, null=True, blank=True)
    unknown_person = models.ForeignKey(UnknownPerson, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=100)  # e.g., camera name
    timestamp = models.DateTimeField(default=timezone.now)
    captured_at = models.DateTimeField(null=True, blank=True)
    latency = models.FloatField(null=True, blank=True)  # in seconds
    
    class Meta:
        ordering = ['-timestamp']  # newest first