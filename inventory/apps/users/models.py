"""
User Models: Custom User, UserRole
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager for User model
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('active', True)
        extra_fields.setdefault('verified_status', 'verified')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the system
    """
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    staff_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    id_picture = models.ImageField(upload_to='id_cards/', blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)

    dept = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    location = models.ForeignKey(
        'locations.Village',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    cfms_ref = models.CharField(max_length=100, blank=True, null=True, unique=True)
    verified_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Required for Django admin
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"

    def save(self, *args, **kwargs):
        # Update last_login on save if not set
        if self.last_login is None and self.pk:
            self.last_login = timezone.now()
        super().save(*args, **kwargs)


class UserRole(models.Model):
    """
    Many-to-many relationship between Users and Roles
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        'rbac.Role',
        on_delete=models.CASCADE,
        related_name='role_users'
    )

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.name} - {self.role.name}"
