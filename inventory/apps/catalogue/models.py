"""
Catalogue Models: Master item definitions
"""
from django.db import models


class ItemInfo(models.Model):
    """
    Master catalogue of item types/definitions
    This defines the types of items that can be tracked in the system
    """
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, blank=True, null=True)
    perishability = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    resource_type = models.CharField(max_length=100, blank=True, null=True)
    activity_name = models.CharField(max_length=255, blank=True, null=True)
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated tags")
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'item_info'
        ordering = ['item_name']
        verbose_name = 'Item Definition'
        verbose_name_plural = 'Item Definitions'

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    @property
    def tag_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

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

    item_info = models.ForeignKey(
        ItemInfo,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    key = models.CharField(max_length=100)
    datatype = models.CharField(max_length=20, choices=DATATYPE_CHOICES, default='string')
    class Meta:
        db_table = 'item_attributes'
        ordering = ['item_info', 'key']
        unique_together = ('item_info', 'key')
    
    def __str__(self):
        return f"{self.item_info.id} - {self.key}" 

