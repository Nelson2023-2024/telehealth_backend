from django.contrib import admin

from .models import State, Country


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "description",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "code", "description")
    list_filter = ("is_active", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "description",
        "state",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "code", "description")
    list_filter = ("state", "is_active", "created_at")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)