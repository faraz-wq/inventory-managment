"""
Department Models
"""
from django.db import models


class Department(models.Model):
    """
    Represents a department/organization in the system
    """
    org_code = models.CharField(max_length=50, unique=True)
    org_shortname = models.CharField(max_length=100)
    org_type = models.CharField(max_length=100, blank=True, null=True)
    org_name = models.CharField(max_length=255)
    report_org = models.CharField(max_length=255, blank=True, null=True)
    agency_address = models.TextField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_designation = models.CharField(max_length=255, blank=True, null=True)
    contact_person_address = models.TextField(blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        ordering = ['org_name']

    def __str__(self):
        return f"{self.org_shortname} - {self.org_name}"


class DepartmentContact(models.Model):
    """
    Contact information for departments
    Supports multiple contact types: telephone, mobile, fax, email
    """
    CONTACT_TYPE_CHOICES = [
        ('telephone', 'Telephone'),
        ('mobile', 'Mobile'),
        ('fax', 'Fax'),
        ('email', 'Email'),
    ]

    dept = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    contact_value = models.CharField(max_length=255)

    class Meta:
        db_table = 'department_contacts'
        ordering = ['dept', 'contact_type']

    def __str__(self):
        return f"{self.dept.org_shortname} - {self.contact_type}: {self.contact_value}"
