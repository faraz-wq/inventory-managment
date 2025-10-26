"""
Item Signals for automatic logging
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Item
from apps.logs.models import Log


@receiver(post_save, sender=Item)
def log_item_save(sender, instance, created, **kwargs):
    """
    Log item creation and updates
    """
    if created:
        # Log item creation
        Log.objects.create(
            user=instance.created_by,
            subject_type='Item',
            subject_id=instance.id,
            action='create',
            status='success',
            metadata={
                'item_name': instance.iteminfo.item_name,
                'dept': instance.dept.org_shortname,
                'status': instance.status
            }
        )
    else:
        # Log item update
        Log.objects.create(
            user=instance.verified_by if instance.verified_by else instance.created_by,
            subject_type='Item',
            subject_id=instance.id,
            action='update',
            status='success',
            metadata={
                'item_name': instance.iteminfo.item_name,
                'status': instance.status,
                'verified_by': instance.verified_by.name if instance.verified_by else None
            }
        )


@receiver(post_delete, sender=Item)
def log_item_delete(sender, instance, **kwargs):
    """
    Log item deletion
    """
    Log.objects.create(
        user=instance.created_by,
        subject_type='Item',
        subject_id=instance.id,
        action='delete',
        status='success',
        metadata={
            'item_name': instance.iteminfo.item_name,
            'dept': instance.dept.org_shortname
        }
    )
