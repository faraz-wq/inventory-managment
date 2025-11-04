"""
BorrowRecord Models: Track borrowed items and borrower information
"""
from django.db import models
from django.conf import settings


class BorrowRecord(models.Model):
    """
    Tracks borrowed items and the person who borrowed them
    """
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ]

    # Item reference
    item = models.ForeignKey(
        'items.Item',
        on_delete=models.CASCADE,
        related_name='borrow_records'
    )

    # Borrower personal details
    borrower_name = models.CharField(max_length=255, help_text="Full name of the borrower")
    aadhar_card = models.CharField(max_length=12, help_text="12-digit Aadhar card number")
    phone_number = models.CharField(max_length=15, help_text="Contact phone number")
    address = models.TextField(help_text="Full address of the borrower")

    # Borrower organizational details (using existing models)
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_items',
        help_text="Department of the borrower"
    )
    location = models.ForeignKey(
        'locations.Village',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrower_locations',
        help_text="Village/location of the borrower"
    )

    # Borrow tracking
    borrow_date = models.DateTimeField(auto_now_add=True, help_text="Date and time when item was borrowed")
    expected_return_date = models.DateField(null=True, blank=True, help_text="Expected date of return")
    actual_return_date = models.DateTimeField(null=True, blank=True, help_text="Actual date and time of return")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')

    # Additional notes
    borrow_notes = models.TextField(blank=True, null=True, help_text="Notes when borrowing")
    return_notes = models.TextField(blank=True, null=True, help_text="Notes when returning")

    # Track who processed this record
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_borrow_records',
        help_text="User who issued the item"
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_borrow_records',
        help_text="User who received the returned item"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'borrow_records'
        ordering = ['-borrow_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['borrow_date']),
            models.Index(fields=['aadhar_card']),
        ]

    def __str__(self):
        return f"{self.borrower_name} - {self.item.iteminfo.item_name if self.item and self.item.iteminfo else 'Unknown Item'} ({self.status})"

    def save(self, *args, **kwargs):
        """
        Override save to automatically update item status
        """
        super().save(*args, **kwargs)

        # Update item status based on borrow record status
        if self.item:
            if self.status == 'borrowed':
                self.item.status = 'borrowed'
            elif self.status == 'returned':
                # When returned, set back to available
                self.item.status = 'available'
            self.item.save()
