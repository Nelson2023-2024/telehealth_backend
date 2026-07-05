from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ConsultantProfile,
    ConsultantReview,
    ConsultantAvailability,
    Speciality,
)
from authentication.serializers import UserSerializer
from base.serializers import BaseModelSerializer, GenericBaseModelSerializer

User = get_user_model()


class SpecialitySerializer(GenericBaseModelSerializer):
    class Meta:
        model = Speciality
        fields = GenericBaseModelSerializer.Meta.fields + ["icon"]


# Whenever a Django field has choices=, Django auto-generates a method called get_<field_name>_display()
class ConsultantAvailabilitySerializer(BaseModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = ConsultantAvailability
        fields = BaseModelSerializer.Meta.fields + [
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
        ]


class ConsultantReviewSerializer(BaseModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = ConsultantReview
        fields = BaseModelSerializer.Meta.fields + [
            "patient_name",
            "rating",
            "review_text",
            "is_verified_consultation",
            "is_anonymous",
        ]

    def get_patient_name(self, obj: ConsultantReview):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.patient.full_name


class ConsultantProfileListSerializer(BaseModelSerializer):
    user = UserSerializer(read_only=True)
    speciality = SpecialitySerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    rating = serializers.DecimalField(
        max_digits=3, decimal_places=2, coerce_to_string=False, default=0.0
    )
    consultation_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False, default=0.0
    )
    years_of_experience = serializers.IntegerField(default=0)
    consultation_duration = serializers.IntegerField(default=30)
    total_consultations = serializers.IntegerField(default=0)
    total_reviews = serializers.IntegerField(default=0)

    class Meta:
        model = ConsultantProfile
        fields = BaseModelSerializer.Meta.fields + [
            "user",
            "speciality",
            "bio",
            "years_of_experience",
            "avatar_url",
            "rating",
            "total_consultations",
            "total_reviews",
            "consultation_fee",
            "consultation_duration",
            "consultation_types",
            "is_verified",
            "is_available",
            "is_featured",
        ]

    def get_avatar_url(self, obj: ConsultantProfile):
        if obj.avatar:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.avatar.url)
                if request
                else obj.avatar.url
            )
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["rating"] = float(instance.rating or 0.0)
        data["consultation_fee"] = float(instance.consultation_fee or 0.0)
        data["years_of_experience"] = int(instance.years_of_experience or 0.0)
        data["consultation_duration"] = int(instance.consultation_duration or 0.0)
        data["total_consultations"] = int(instance.total_consultations or 0)
        data["total_reviews"] = int(instance.total_reviews or 0)

        data["board_certifications"] = [
            str(x) for x in (instance.board_certifications or []) if x
        ]

        data["additional_qualifications"] = [
            str(x) for x in (instance.additional_qualifications or []) if x
        ]

        data["languages_spoken"] = [
            str(x) for x in (instance.languages_spoken or []) if x
        ]

        data["consultation_types"] = instance.consultation_types or "all"

        return data


class ConsultantProfileDetailSerializer(ConsultantProfileListSerializer):
    recent_reviews = ConsultantReviewSerializer(
        source="reviews", many=True, read_only=True
    )
    availability_slots = ConsultantAvailabilitySerializer(many=True, read_only=True)

    license_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    medical_degree = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    phone_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    clinic_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    clinic_address = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    clinic_city = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    clinic_country = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta(ConsultantProfileListSerializer.Meta):
        fields = ConsultantProfileListSerializer.Meta.fields + [
            "license_number",
            "medical_degree",
            "board_certifications",
            "additional_qualifications",
            "phone_number",
            "clinic_name",
            "clinic_address",
            "clinic_city",
            "clinic_country",
            "languages_spoken",
            "availability_schedule",
            "recent_reviews",
            "availability_slots",
            "verification_date",
        ]


class ConsultantProfileUpdateSerializer(BaseModelSerializer):
    availabilty_slots = ConsultantAvailabilitySerializer(many=True, required=False)
    consultation_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=0.0
    )
    years_of_experience = serializers.IntegerField(required=False, default=0)
    consultation_duration = serializers.IntegerField(required=False, default=30)

    class Meta:
        model = ConsultantProfile
        fields = BaseModelSerializer.Meta.fields + [
            "bio",
            "years_of_experience",
            "medical_degree",
            "board_certifications",
            "additional_qualifications",
            "phone_number",
            "clinic_name",
            "clinic_address",
            "clinic_city",
            "clinic_country",
            "consultaion_fee",
            "consultation_duration",
            "consultation_types",
            "languages_spoken",
            "availability_schedule",
            "is_available",
            "availability_slots",
        ]

    def validate_consultation_fee(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Consultation fee cannot be negative")
        return value or 0.0

    def validate_years_of_experience(self, value):
        if value is not None and (value < 0 or value > 50):
            raise serializers.ValidationError("Years of experience be between 0 and 50")
        return value or 0

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["consultation_fee"] = float(instance.consultation_fee or 0.0)
        data["years_of_experience"] = int(instance.years_of_experience or 0)
        data["consultation_duration"] = int(instance.consultation_duration or 30)

        return data


class ConsultantProfileCreateSerializer(BaseModelSerializer):
    speciality_id = serializers.IntegerField(write_only=True)
    consultation_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    years_of_experience = serializers.IntegerField(default=0)
    consultation_duration = serializers.IntegerField(default=30)

    class Meta:
        model = ConsultantProfile
        fields = BaseModelSerializer.Meta.fields + [
            "speciality_id",
            "license_number",
            "bio",
            "years_of_experience",
            "medical_degree",
            "board_certifications",
            "additional_qualifications",
            "phone_number",
            "clinic_name",
            "clinic_address",
            "clinic_city",
            "clinic_country",
            "consultation_fee",
            "consultation_duration",
            "consultation_types",
            "languages_spoken",
        ]


class ConsultantReviewCreateSerializer(BaseModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = ConsultantReview
        fields = BaseModelSerializer.Meta.fields + [
            "rating",
            "review_text",
            "is_anonymous",
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
