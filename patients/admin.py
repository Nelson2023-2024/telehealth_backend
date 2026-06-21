from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import PatientProfile, PatientMedicalHistory


class PatientMedicalHistoryInline(admin.TabularInline):
    """Inline for medical history records within PatientProfile"""

    model = PatientMedicalHistory
    extra = 1
    fields = (
        "record_type",
        "title",
        "description",
        "date_occurred",
        "healthcare_provider",
        "attachments",
    )
    ordering = ("-date_occurred", "-created_at")
    readonly_fields = ("created_at", "updated_at")
    can_delete = True


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "phone_number",
        "gender",
        "blood_type",
        "age_display",
        "country",
        "created_at",
    )
    list_filter = (
        "gender",
        "blood_type",
        "country",
        "share_medical_history",
        "allow_emergency_access",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone_number",
        "city",
        "emergency_contact_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "avatar_preview",
        "age_display",
    )
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("user", "avatar", "avatar_preview")}),
        (
            "Personal Information",
            {
                "fields": (
                    "bio",
                    "date_of_birth",
                    "age_display",
                    "gender",
                    "phone_number",
                )
            },
        ),
        ("Location", {"fields": ("address", "city", "country", "postal_code")}),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                )
            },
        ),
        (
            "Medical Details",
            {
                "fields": (
                    "blood_type",
                    "allergies",
                    "chronic_conditions",
                    "current_medications",
                    "medical_notes",
                )
            },
        ),
        (
            "Privacy & Preferences",
            {
                "fields": (
                    "share_medical_history",
                    "allow_emergency_access",
                    "preferred_language",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [PatientMedicalHistoryInline]
    actions = ["enable_share_medical_history", "disable_share_medical_history"]

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:50%;" />',
                obj.avatar.url,
            )
        return "No image"

    avatar_preview.short_description = "Avatar Preview"

    def age_display(self, obj):
        age = obj.age
        if age is not None:
            return f"{age} years"
        return "—"

    age_display.short_description = "Age"

    def enable_share_medical_history(self, request, queryset):
        updated = queryset.update(share_medical_history=True)
        self.message_user(
            request, f"{updated} patient(s) enabled medical history sharing."
        )

    enable_share_medical_history.short_description = "Enable medical history sharing"

    def disable_share_medical_history(self, request, queryset):
        updated = queryset.update(share_medical_history=False)
        self.message_user(
            request, f"{updated} patient(s) disabled medical history sharing."
        )

    disable_share_medical_history.short_description = "Disable medical history sharing"


@admin.register(PatientMedicalHistory)
class PatientMedicalHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "record_type",
        "title",
        "date_occurred",
        "healthcare_provider",
        "created_at",
    )
    list_filter = ("record_type", "date_occurred", "created_at")
    search_fields = (
        "patient__user__email",
        "patient__user__first_name",
        "patient__user__last_name",
        "title",
        "description",
        "healthcare_provider",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-date_occurred", "-created_at")
    fieldsets = (
        (None, {"fields": ("patient", "record_type", "title")}),
        (
            "Details",
            {"fields": ("description", "date_occurred", "healthcare_provider")},
        ),
        ("Attachments", {"fields": ("attachments",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
