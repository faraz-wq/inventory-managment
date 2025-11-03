"""
Location Models: District, Mandal, Village hierarchy
"""
from django.db import models


class District(models.Model):
    """
    Represents a district (top-level administrative division)
    """
    district_name = models.CharField(max_length=255)
    district_code_ap = models.CharField(max_length=50,  blank=True, null=True)
    district_code_ind = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'districts'
        ordering = ['district_name']

    def __str__(self):
        return f"{self.district_name} ({self.district_code_ap})"


class Mandal(models.Model):
    """
    Represents a mandal (subdivision within a district)
    """
    mandal_name = models.CharField(max_length=255)
    mandal_code_ap = models.CharField(max_length=50,  blank=True, null=True)
    mandal_code_ind = models.CharField(max_length=50, blank=True, null=True)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='mandals'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'mandals'
        ordering = ['district', 'mandal_name']

    def __str__(self):
        return f"{self.mandal_name}, {self.district.district_name}"


class Village(models.Model):
    """
    Represents a village (lowest-level administrative division)
    """
    village_name = models.CharField(max_length=255)
    village_code_ap = models.CharField(max_length=50,  blank=True, null=True)
    village_code_ind = models.CharField(max_length=50, blank=True, null=True)
    mandal = models.ForeignKey(
        Mandal,
        on_delete=models.CASCADE,
        related_name='villages'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='villages'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'villages'
        ordering = ['district', 'mandal', 'village_name']

    def __str__(self):
        return f"{self.village_name}, {self.mandal.mandal_name}, {self.district.district_name}"
