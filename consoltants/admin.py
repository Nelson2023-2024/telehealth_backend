from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Speciality,
    ConsultantProfile,
    ConsultantReview,
    ConsultantAvailability,
)


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "icon", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


class ConsultantAvailabilityInline(admin.TabularInline):
    """Inline for availability slots within ConsultantProfile"""

    model = ConsultantAvailability
    extra = 1
    fields = ("day_of_week", "start_time", "end_time")
    ordering = ("day_of_week", "start_time")


class ConsultantReviewInline(admin.TabularInline):
    """Inline for reviews within ConsultantProfile (read‑only)"""

    model = ConsultantReview
    extra = 0
    fields = (
        "patient",
        "rating",
        "review_text",
        "is_verified_consultation",
        "created_at",
    )
    readonly_fields = (
        "patient",
        "rating",
        "review_text",
        "is_verified_consultation",
        "created_at",
    )
    can_delete = False
    show_change_link = True


@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "speciality",
        "is_verified",
        "is_available",
        "is_featured",
        "rating",
        "total_consultations",
        "consultation_fee",
        "created_at",
    )
    list_filter = (
        "speciality",
        "is_verified",
        "is_available",
        "is_featured",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "license_number",
        "clinic_name",
        "clinic_city",
    )
    readonly_fields = (
        "rating",
        "total_consultations",
        "total_reviews",
        "created_at",
        "updated_at",
        "verification_date",
        "avatar_preview",
    )
    ordering = ("-rating", "-created_at")
    fieldsets = (
        (None, {"fields": ("user", "speciality")}),
        (
            "Personal Details",
            {"fields": ("avatar", "avatar_preview", "bio", "years_of_experience")},
        ),
        (
            "Credentials",
            {
                "fields": (
                    "license_number",
                    "medical_degree",
                    "board_certifications",
                    "additional_qualifications",
                )
            },
        ),
        (
            "Contact & Clinic",
            {
                "fields": (
                    "phone_number",
                    "clinic_name",
                    "clinic_address",
                    "clinic_city",
                    "clinic_country",
                )
            },
        ),
        (
            "Consultation Settings",
            {
                "fields": (
                    "consultation_fee",
                    "consultation_duration",
                    "consultation_types",
                    "languages_spoken",
                )
            },
        ),
        (
            "Availability & Status",
            {"fields": ("is_available", "availability_schedule")},
        ),
        (
            "Verification & Featured",
            {"fields": ("is_verified", "verification_date", "is_featured")},
        ),
        ("Statistics", {"fields": ("rating", "total_consultations", "total_reviews")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [ConsultantAvailabilityInline, ConsultantReviewInline]
    actions = [
        "verify_selected",
        "feature_selected",
        "make_available",
        "make_unavailable",
    ]

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:50%;" />',
                obj.avatar.url,
            )
        return "No image"

    avatar_preview.short_description = "Avatar Preview"

    def verify_selected(self, request, queryset):
        count = 0
        for profile in queryset:
            if not profile.is_verified:
                profile.verify_consultant()
                count += 1
        self.message_user(request, f"{count} consultant(s) verified.")

    verify_selected.short_description = "Verify selected consultants"

    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} consultant(s) marked as featured.")

    feature_selected.short_description = "Mark selected consultants as featured"

    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f"{updated} consultant(s) set as available.")

    make_available.short_description = "Set selected as available"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f"{updated} consultant(s) set as unavailable.")

    make_unavailable.short_description = "Set selected as unavailable"


@admin.register(ConsultantReview)
class ConsultantReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "consultant",
        "patient",
        "rating_stars",
        "review_preview",
        "is_verified_consultation",
        "is_anonymous",
        "created_at",
    )
    list_filter = ("rating", "is_verified_consultation", "is_anonymous", "created_at")
    search_fields = (
        "consultant__user__email",
        "consultant__user__first_name",
        "consultant__user__last_name",
        "patient__email",
        "patient__first_name",
        "patient__last_name",
        "review_text",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def rating_stars(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html('<span style="color: #f5b342;">{}</span>', stars)

    rating_stars.short_description = "Rating"

    def review_preview(self, obj):
        return (
            obj.review_text[:50] + "…"
            if obj.review_text and len(obj.review_text) > 50
            else obj.review_text
        )

    review_preview.short_description = "Review (preview)"


@admin.register(ConsultantAvailability)
class ConsultantAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "consultant",
        "day_display",
        "start_time",
        "end_time",
        "created_at",
    )
    list_filter = ("day_of_week", "consultant")
    search_fields = (
        "consultant__user__email",
        "consultant__user__first_name",
        "consultant__user__last_name",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("consultant", "day_of_week", "start_time")

    def day_display(self, obj):
        return obj.get_day_of_week_display()

    day_display.short_description = "Day"
    day_display.admin_order_field = "day_of_week"
