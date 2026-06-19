"""
Base serializer all model serializers inherit common fields from.
"""

from rest_framework import serializers

"""
Job 1 — incoming data (request): JSON → Python/Django object
Job 2 — outgoing data (response): Django object → JSON

# Input-only serializers (registration, login, password reset, search filters)
# → inherit plain serializers.Serializer or serializers.ModelSerializer directly

# Output/representation serializers (returning model data in API responses)
# → inherit BaseModelSerializer or GenericBaseModelSerializer
"""


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Provides the common fields every model has via BaseModel.
    Inherit this instead of serializers.ModelSerializer directly.
    """

    # source='state.name' — tells DRF to reach into the related State object and pull its name field directly,
    # so the API response shows the state name instead of just the ID:
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        abstract = True
        fields = ["id", "is_active", "state", "state_name", "created_at", "updated_at"]


class GenericBaseModelSerializer(BaseModelSerializer):
    """
    Provides common fields for models inheriting GenericBaseModel (name, description).
    """

    class Meta(BaseModelSerializer.Meta):
        abstract = True
        fields = BaseModelSerializer.Meta.fields + ["name", "description"]
