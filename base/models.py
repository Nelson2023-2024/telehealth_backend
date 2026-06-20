from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _


# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("ID")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    state = models.ForeignKey(
        "base.State",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
        verbose_name=_("State"),
        help_text=_("The current state of this record"),
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["state"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_active", "state"]),
        ]


class GenericBaseModel(BaseModel):
    name = models.CharField(
        blank=True, null=True, max_length=30, verbose_name=_("Name")
    )
    code = models.CharField(
        blank=True, null=True, max_length=30, unique=True,
        verbose_name=_("Code"),
        help_text=_("Stable identifier for lookups, unaffected by renaming 'name'")
    )
    description = models.TextField(
        max_length=255, blank=True, null=True, verbose_name=_("Description")
    )

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return "%s" % self.name


class State(GenericBaseModel):
    """
    Defines the different states used across the system e.g. Active, Verified, Suspended.
    Stored in the database so new states can be added without schema changes.
    """

    class Meta:
        db_table = "states"
        ordering = ("name",)
        verbose_name = _("State")
        verbose_name_plural = _("States")

    @classmethod
    def default_state(cls):
        """
        Returns the Active state id — used as the default for ForeignKey fields.
        Creates it if it doesn't exist yet.
        """
        state, created = cls.objects.get_or_create(
            name="Active", defaults={"description": "Record is active and operational"}
        )
        return state.id

    @classmethod
    def disabled_state(cls):
        """
        Returns the Disabled state id — used to soft-disable records without deleting them.
        Creates it if it doesn't exist yet.
        """
        state, created = cls.objects.get_or_create(
            name="Disabled",
            defaults={"description": "Record is disabled and no longer operational"},
        )
        return state.id


class Country(GenericBaseModel):
    class Meta:
        abstract = False
        db_table = "countries"
        ordering = ("name",)
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
