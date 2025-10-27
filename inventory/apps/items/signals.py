"""
Item Signals for automatic logging - ENHANCED
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Item
from apps.logs.models import Log

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Item)
def track_item_changes(sender, instance, **kwargs):
    """
    Track changes before saving to log what fields were modified
    """
    if instance.pk:
        try:
            old_instance = Item.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_verified_by = old_instance.verified_by
        except Item.DoesNotExist:
            pass


@receiver(post_save, sender=Item)
def log_item_save(sender, instance, created, **kwargs):
    """
    Log item creation and updates with error handling
    """
    try:
        with transaction.atomic():
            if created:
                log_item_creation(instance)
            else:
                log_item_update(instance)
    except Exception as e:
        logger.error(f"Failed to log item save: {e}", exc_info=True)


def log_item_creation(instance):
    """Log item creation"""
    user = getattr(instance, 'created_by', None)
    if not user:
        logger.warning(f"Item {instance.id} created without created_by user")
        return

    metadata = {
        'item_name': get_item_name(instance),
        'dept': get_dept_name(instance),
        'status': instance.status,
        'iteminfo_id': instance.iteminfo_id
    }

    Log.objects.create(
        user=user,
        subject_type='Item',
        subject_id=instance.id,
        action='create',
        status='success',
        metadata=metadata
    )
    logger.info(f"Item {instance.id} created by user {user.staff_id}")


def log_item_update(instance):
    """Log item updates with change detection"""
    # Determine who performed the update
    user = getattr(instance, 'verified_by', None) or getattr(instance, 'created_by', None)
    if not user:
        logger.warning(f"Item {instance.id} updated without user context")
        return

    metadata = {
        'item_name': get_item_name(instance),
        'status': instance.status,
        'iteminfo_id': instance.iteminfo_id,
        'dept_id': instance.dept_id
    }

    # Track specific changes if available
    if hasattr(instance, '_old_status'):
        if instance._old_status != instance.status:
            metadata['status_changed'] = {
                'from': instance._old_status,
                'to': instance.status
            }

    if hasattr(instance, '_old_verified_by'):
        if instance._old_verified_by != instance.verified_by_id:
            metadata['verification_changed'] = True

    Log.objects.create(
        user=user,
        subject_type='Item',
        subject_id=instance.id,
        action='update',
        status='success',
        metadata=metadata
    )
    logger.info(f"Item {instance.id} updated by user {user.staff_id}")


@receiver(post_delete, sender=Item)
def log_item_delete(sender, instance, **kwargs):
    """
    Log item deletion with error handling
    """
    try:
        user = getattr(instance, 'created_by', None)
        if not user:
            logger.warning(f"Item {instance.id} deleted without created_by user")
            return

        metadata = {
            'item_name': get_item_name(instance),
            'dept': get_dept_name(instance),
            'iteminfo_id': instance.iteminfo_id
        }

        Log.objects.create(
            user=user,
            subject_type='Item',
            subject_id=instance.id,
            action='delete',
            status='success',
            metadata=metadata
        )
        logger.info(f"Item {instance.id} deleted by user {user.staff_id}")

    except Exception as e:
        logger.error(f"Failed to log item deletion: {e}", exc_info=True)


# Helper functions to safely get related object attributes
def get_item_name(instance):
    """Safely get item name from related ItemInfo"""
    try:
        return instance.iteminfo.item_name
    except (ItemInfo.DoesNotExist, AttributeError):
        return "Unknown Item"


def get_dept_name(instance):
    """Safely get department name"""
    try:
        return instance.dept.org_shortname
    except (Department.DoesNotExist, AttributeError):
        return "Unknown Department"


def get_user_name(user):
    """Safely get user name"""
    if user and hasattr(user, 'name'):
        return user.name
    return "Unknown User"