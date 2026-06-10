from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

# BaseUserManager — base class you extend to build your custom manager
# AbstractBaseUser — base class for your custom User model (used later)
# PermissionsMixin — adds is_superuser, groups, and permissions support

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

    def get_patients(self):
        return self.filter(role='patient', is_active=True)

    def get_consultants(self):
        return self.filter(role='consultant', is_active=True)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('consultant', 'Consultant'),
        ('admin', 'Admin')
    ]

    # Basic Fields
    email = models.EmailField(unique=True, db_index=True, verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient', db_index=True)

    # Status Fields
    is_staff = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Timestamps
    last_seen = models.DateTimeField(default=timezone.now)
    email_verified_at = models.DateTimeField(null= True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['is_online'])
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def mark_email_verified(self):
        self.is_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'email_verified_at'])

    def update_online_status(self, is_online = True):
        self.is_online = is_online
        self.last_seen = timezone.now()
        self.save(update_fields=['is_online','last_seen'])







