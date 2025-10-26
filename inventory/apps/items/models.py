"""
Item Models: Item and ItemAttribute
"""
from django.db import models
from django.conf import settings


class Item(models.Model):
    """
    Represents a physical item/asset in the system
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('available', 'Available'),
    ]

    photo = models.ImageField(upload_to='items/', blank=True, null=True)
    eol_date = models.DateField(blank=True, null=True, help_text="End of life date")
    operational_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Relationships
    geocode = models.ForeignKey(
        'locations.Village',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    iteminfo = models.ForeignKey(
        'catalogue.ItemInfo',
        on_delete=models.CASCADE,
        related_name='items'
    )
    dept = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='dept_items'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_items'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_items'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_items'
    )

    # Geographic coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.iteminfo.item_name} - {self.status}"


class ItemAttribute(models.Model):
    """
    Dynamic key-value attributes for items
    Allows flexible metadata storage for different item types
    """
    DATATYPE_CHOICES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('json', 'JSON'),
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    key = models.CharField(max_length=100)
    value = models.TextField()
    datatype = models.CharField(max_length=20, choices=DATATYPE_CHOICES, default='string')

    class Meta:
        db_table = 'item_attributes'
        ordering = ['item', 'key']

    def __str__(self):
        return f"{self.item.id} - {self.key}: {self.value}"
