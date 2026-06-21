from django.db import models
from base.models import BaseModel, GenericBaseModel
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

# BaseUserManager — base class you extend to build your custom manager
# AbstractBaseUser — base class for your custom User model (used later)
# PermissionsMixin — adds is_superuser, groups, and permissions support


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        admin_role, _ = Role.objects.get_or_create(name="Admin")
        extra_fields.setdefault("role", admin_role)
        return self.create_user(email, password, **extra_fields)

    def get_patients(self):
        return self.filter(role="patient", is_active=True)

    def get_consultants(self):
        return self.filter(role="consultant", is_active=True)


class Permission(GenericBaseModel):
    class Meta:
        db_table = "permissions"
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")

    def __str__(self):
        return self.name


class Role(GenericBaseModel):
    permissions = models.ManyToManyField(
        Permission, blank=True, related_name="roles", verbose_name=_("Permissions")
    )

    class Meta:
        db_table = "roles"
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    # Basic Fields
    email = models.EmailField(
        unique=True, db_index=True, verbose_name=_("Email Address")
    )
    first_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("First Name")
    )
    last_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Last Name")
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    # Status Fields
    is_staff = models.BooleanField(default=False, verbose_name=_("Staff Member"))
    is_online = models.BooleanField(default=False, verbose_name=_("Online Status"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Email Verified"))

    # Timestamps
    last_seen = models.DateTimeField(
        default=timezone.now, verbose_name=_("Last Seen At")
    )
    email_verified_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Email Verified At")
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_online"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def mark_email_verified(self):
        self.is_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=["is_verified", "email_verified_at"])

    def update_online_status(self, is_online=True):
        self.is_online = is_online
        self.last_seen = timezone.now()
        self.save(update_fields=["is_online", "last_seen"])


class EmailVerificationToken(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
        verbose_name=_("User"),
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Verification Token"),
    )
    is_used = models.BooleanField(default=False, verbose_name=_("Token Used"))

    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Expires At")
    )

    class Meta:
        db_table = "email_verification_tokens"
        indexes = [
            # unique=True already creates an index, so this in Meta is redundant:
            # models.Index(fields=['token']),
            models.Index(
                fields=["user", "is_used"]
            )  # # fast "get unused tokens for user"
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        """checks is_used AND is_expired() together"""
        return not self.is_used and not self.is_expired()
