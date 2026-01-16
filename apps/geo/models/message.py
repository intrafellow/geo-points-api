from django.conf import settings
from django.db import models

from .point import Point


class Message(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="geo_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "geo_messages"
        indexes = [models.Index(fields=["point", "created_at"])]
