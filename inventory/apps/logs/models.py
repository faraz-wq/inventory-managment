"""
Log Models: Activity tracking
"""
from django.db import models
from django.conf import settings


class Log(models.Model):
    """
    Represents an activity log entry in the system
    Tracks all CRUD operations and important actions
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    subject_type = models.CharField(
        max_length=50,
        help_text="Type of object being logged (e.g., Item, User, Department)"
    )
    subject_id = models.IntegerField(
        help_text="ID of the object being logged"
    )
    action = models.CharField(
        max_length=50,
        help_text="Action performed (e.g., create, update, delete, verify)"
    )
    status = models.CharField(
        max_length=20,
        help_text="Status of the action (e.g., success, failure)"
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional metadata about the action"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['subject_type', 'subject_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_name = self.user.name if self.user else 'System'
        return f"{user_name} - {self.action} {self.subject_type} #{self.subject_id}"
