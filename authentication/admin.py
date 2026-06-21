from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    User,
    Role,
    Permission,
    EmailVerificationToken,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
        "state__code",
    )
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "state__code", "description")
    search_fields = ("name",)
    filter_horizontal = ("permissions",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "role",
        "is_active",
        "is_staff",
        "is_verified",
        "is_online",
        "state__code",
        "last_seen",
        "created_at",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_verified",
        "is_online",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_seen",
        "email_verified_at",
        "password",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        (
            "Status",
            {
                "fields": (
                    "is_online",
                    "last_seen",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                )
            },
        ),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def is_online_status(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">●</span> Online')
        return format_html('<span style="color: red;">●</span> Offline')

    is_online_status.short_description = "Status"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    actions = ["make_active", "make_inactive"]

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"{updated} users were successfully marked as active."
        )

    make_active.short_description = "Mark selected users as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} users were successfully marked as inactive."
        )

    make_inactive.short_description = "Mark selected users as inactive"


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token",
        "is_used",
        "expires_at",
        "created_at",
    )

    list_filter = ("is_used", "expires_at", "created_at")

    search_fields = (
        "user__email",
        "user__last_name",
        "user__first_name",
        "token",
    )

    readonly_fields = (
        "token",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    def token_preview(self, obj):
        return f"{str(obj.token)[:8]}..."

    token_preview.short_description = "Token Preview"

    def is_expired_status(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')

    is_expired_status.short_description = "Status"

    actions = ["mark_tokens_used"]

    def mark_tokens_used(self, request, queryset):
        count = queryset.filter(is_used=False).update(is_used=True)
        self.message_user(request, f"{count} tokens marked as used.")

    mark_tokens_used.short_description = "Mark selected tokens as used"
