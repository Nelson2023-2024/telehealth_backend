from django.db import models
from django.contrib.auth import get_user_model
from base.models import BaseModel, GenericBaseModel, Country
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

User = get_user_model()

phone_regex = RegexValidator(
    regex=r"^\+[1-9]\d{6,14}$",
    message=_(
        "Phone number must include country code e.g. '+254712345678', "
        "'+12125552368', '+441234567890'. Between 7 and 15 digits after '+'."
    ),
)


# Create your models here.
class Speciality(GenericBaseModel):
    """Medical specialities"""

    icon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_plural_name = "Specialties"
        db_table = "specialities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ConsultantProfile(BaseModel):
    """Consultant-specific profile information"""

    CONSULTATION_TYPE_CHOICES = [
        ("video", "Video Consultation"),
        ("audio", "Audio Only"),
        ("chat", "Text Chat"),
        ("all", "All Types"),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="consultant_profile",
        limit_choices_to={"role__name": "consultant"},
    )
    speciality = models.ForeignKey(
        Speciality, on_delete=models.PROTECT, related_name="consultants"
    )

    avatar = models.ImageField(upload_to="consultants/avatars/", blank=True, null=True)
    bio = models.TextField(
        max_length=1000, blank=True, null=True, verbose_name=_("Biography")
    )
    years_of_experience = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        validators=[MaxValueValidator(50)],
        verbose_name=_("Years of Experience"),
    )

    license_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("License Number"),
    )
    medical_degree = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Medical Degree")
    )
    board_certifications = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Board Certifications"),
        help_text=_("List of board certifications"),
    )
    additional_qualifications = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Additional Qualifications"),
        help_text=_("List of additional qualifications"),
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
        help_text=_("Include country code e.g. +254712345678"),
    )
    clinic_name = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Clinic Name")
    )
    clinic_address = models.TextField(
        max_length=500, blank=True, null=True, verbose_name=_("Clinic Address")
    )
    clinic_city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Clinic City")
    )
    clinic_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Clinic Country"),
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Consultation Fee"),
    )
    consultation_duration = models.PositiveIntegerField(
        default=30,
        blank=True,
        null=True,
        verbose_name=_("Consultation Duration"),
        help_text=_("Default consultation duration in minutes"),
    )

    consultation_types = models.CharField(
        max_length=10,
        choices=CONSULTATION_TYPE_CHOICES,
        default="all",
        blank=True,
        null=True,
        verbose_name=_("Consultation Types"),
    )

    languages_spoken = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Languages Spoken"),
        help_text=_("List of languages the consultant speaks"),
    )

    is_available = models.BooleanField(default=True)
    availability_schedule = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Availability Schedule"),
        help_text="Weekly schedule with time slots",
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("Rating"),
    )
    total_consultations = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name=_("Total Consultations")
    )
    total_reviews = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name=_("Total Reviews")
    )

    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Verification Date")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_("Featured consultants appear at the top of search results"),
    )

    class Meta:
        db_table = "consultant_profiles"
        verbose_name = "Consultant Profile"
        verbose_name_plural = "Consultant Profiles"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["speciality"]),
            models.Index(fields=["is_verified", "is_available"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.speciality.name}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def verify_consultant(self):
        """Mark consultant as verified"""
        self.is_verified = True
        self.verification_date = timezone.now()
        self.save(update_fields=["is_verified", "verification_date"])

    def update_rating(self):
        from django.db.models import Avg

        avg_rating = self.reviews.aggregate(Avg("rating"))["rating__avg"]

        if avg_rating:
            self.rating = round(avg_rating, 2)
            self.save(update_fields=["rating"])

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.user and self.user.role != "consultant":
            raise ValidationError("User must have 'consultant' role")


class ConsultantReview(BaseModel):
    RATING_CHOICES = [(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)]
    consultant = models.ForeignKey(
        ConsultantProfile, on_delete=models.CASCADE, related_name="reviews"
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role__name": "patient"},
        verbose_name=_("Patient"),
    )

    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name=_("Rating"))
    review_text = models.TextField(
        max_length=1000, blank=True, null=True, verbose_name=_("Review")
    )

    is_verified_consultation = models.BooleanField(
        default=False,
        verbose_name=_("Verified Consultation"),
        help_text=_("Review is from a confirmed consultation"),
    )
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name=_("Anonymous"),
        help_text=_("Hide patient name from public view"),
    )

    class Meta:
        db_table = "consultant_reviews"
        unique_together = ["consultant", "patient"]
        ordering = ["-created_at"]
        verbose_name = _("Consultant Review")
        verbose_name_plural = _("Consultant Reviews")
        indexes = [
            models.Index(fields=["consultant", "rating"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_verified_consultation"]),
        ]

    def __str__(self):
        patient_name = "Anonymous" if self.is_anonymous else self.patient.full_name
        return (
            f"{patient_name} → Dr. {self.consultant.user.full_name} ({self.rating} ★)"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.consultant.update_rating()

    def delete(self, *args, **kwargs):
        consultant = self.consultant
        super().delete(*args, **kwargs)
        consultant.update_rating()


class ConsultantAvailability(BaseModel):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="availability_slots",
        verbose_name=_("Consultant"),
    )
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES, verbose_name=_("Day of Week")
    )
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))

    class Meta:
        db_table = "consultant_availability"
        unique_together = ["consultant", "day_of_week", "start_time", "end_time"]
        ordering = ["day_of_week", "start_time"]
        verbose_name = _("Consultant Availability")
        verbose_name_plural = _("Consultant Availabilities")
        indexes = [
            models.Index(
                fields=["consultant", "day_of_week"]
            ),  # get consultant's slots for a day
            models.Index(
                fields=["day_of_week", "start_time"]
            ),  # find all consultants available at a time
        ]

    # TODO
    def __str__(self):
        return (
            f"Dr. {self.consultant.user.full_name} - "
            f"{self.get_day_of_week_display()} "
            f"{self.start_time} - {self.end_time}"
        )

    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError(
                    {"end_time": _("End time must be after start time")}
                )
