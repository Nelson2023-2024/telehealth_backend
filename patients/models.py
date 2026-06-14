from django.db import models
from django.contrib.auth import get_user_model
from base.models import BaseModel, GenericBaseModel, Country
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

# Return the User model that is active in this project.
User = get_user_model()

phone_regex = RegexValidator(
    regex=r"^\+[1-9]\d{6,14}$",
    message=_(
        "Phone number must include country code e.g. '+254712345678', '+12125552368', '+441234567890'. Between 7 and 15 digits after '+'."
    ),
)


class PatientProfile(BaseModel):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    BLOOD_TYPE_CHOICES = [
        ("A+", "A Positive"),
        ("A-", "A Negative"),
        ("B+", "B Positive"),
        ("B-", "B Negative"),
        ("AB+", "AB Positive"),
        ("AB-", "AB Negative"),
        ("O+", "O Positive"),
        ("O-", "O Negative"),
        ("unknown", "Unknown"),
    ]

    # Todo
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        limit_choices_to={"role__name": "patient"},
        verbose_name=_("User"),
    )
    avatar = models.ImageField(
        upload_to="patients/avatars/",
        blank=True,
        null=True,
        verbose_name=_("Profile Photo"),
    )
    bio = models.TextField(
        max_length=500, blank=True, null=True, verbose_name=_("Biography")
    )
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name=_("Date of Birth")
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Gender"),
    )

    phone_number = models.CharField(
        max_length=17,  # E.164 max is 15 digits + "+" = 16 chars
        validators=[phone_regex],
        verbose_name=_("Phone Number"),
        help_text=_("Include country code e.g. +254712345678"),
    )

    address = models.TextField(
        max_length=300, blank=True, null=True, verbose_name=_("Address")
    )
    city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("City")
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Country"),
    )
    postal_code = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Postal Code")
    )
    emergency_contact_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Emergency Contact Name")
    )
    emergency_contact_phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name=_("Emergency Contact Phone"),
    )
    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Emergency Contact Relationship"),
    )
    blood_type = models.CharField(
        max_length=10,
        choices=BLOOD_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Blood Type"),
    )
    allergies = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Allergies"),
        help_text="List of allergies",
    )
    chronic_conditions = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Chronic Conditions"),
        help_text="List of chronic conditions",
    )
    current_medications = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Current Medications"),
        help_text="List of current medications",
    )
    medical_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Medical Notes"),
        help_text="Additional medical information",
    )

    share_medical_history = models.BooleanField(
        default=True,
        verbose_name=_("Share Medical History"),
        help_text=_("Allow consultants to view medical history"),
    )
    allow_emergency_access = models.BooleanField(
        default=True,
        verbose_name=_("Allow Emergency Access"),
        help_text=_("Allow emergency personnel to access medical information"),
    )
    preferred_language = models.CharField(
        max_length=10, default="en", verbose_name=_("Preferred Language")
    )

    class Meta:
        db_table = "patient_profiles"
        verbose_name = "Patient Profile"
        verbose_name_plural = "Patient Profiles"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["blood_type"]),  # filter patients by blood type
            models.Index(fields=["gender"]),  # filter by gender
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.user.full_name} - Patient Profile"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    @property
    def age(self):
        if not self.date_of_birth:
            return None

        return relativedelta(timezone.now().date(), self.date_of_birth.date()).years

    def clean(self):
        if self.user and self.user.role != "patient":
            raise ValidationError("User must have 'patient' role")


class PatientMedicalHistory(BaseModel):
    RECORD_TYPE_CHOICES = [
        ("diagnosis", "Diagnosis"),
        ("procedure", "Medical Procedure"),
        ("surgery", "Surgery"),
        ("hospitalization", "Hospitalization"),
        ("vaccination", "Vaccination"),
        ("test_result", "Test Result"),
        ("other", "Other"),
    ]
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="medical_history",
        verbose_name=_("Patient"),
    )

    record_type = models.CharField(
        max_length=20, choices=RECORD_TYPE_CHOICES, verbose_name=_("Record Type")
    )
    title = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Title")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    date_occurred = models.DateField(
        blank=True, null=True, verbose_name=_("Date Occurred")
    )
    healthcare_provider = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Healthcare Provider")
    )

    attachments = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Attachments"),
        help_text=_("List of attached file URLs or references"),
    )

    class Meta:
        db_table = "patient_medical_history"
        ordering = ["-date_occurred", "-created_at"]
        indexes = [
            models.Index(fields=["patient"]),
            models.Index(fields=["record_type"]),
            models.Index(fields=["date_occurred"]),
            models.Index(
                fields=["patient", "record_type"]
            ),  # get all diagnoses for a patient
        ]

    def __str__(self):
        return f"{self.patient.user.full_name} - {self.title}"
