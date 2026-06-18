from rest_framework import serializers
from django.contrib.auth import get_user_model
from base.services.services import UserService
from .models import User
from typing import Dict, Any
from base.serializers import BaseModelSerializer

"""
Job 1 — incoming data (request): JSON → Python/Django object
Job 2 — outgoing data (response): Django object → JSON
"""


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registrtion serializer"""
    password = serializers.CharField(write_only=True, min_length=8, label='Password',
                                     error_messages={'min_length': 'Password too short'})
    password_confirm = serializers.CharField(write_only=True, label='Confirm Password',
                                             error_messages={'min_length': 'Password too short'})

    class Meta:
        # tells the serializer which Django model to read field definitions from.
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password',
                  'password_confirm']  # # which fields to expose

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    # validate_<fieldname>() — validates a single field
    def validate_email(self, value):
        if 'gmail' not in value:
            raise serializers.ValidationError("Only Gmail addresses allowed")
        return value

    def validate_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Password cannot be all numbers")
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('password_confirm')
        return UserService().create_user(**validated_data)  # create_user() hashes the password:


class UserSerilizer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    # SerializerMethodField lets you add a custom computed field that doesn't exist directly on the model.
    has_verified_email = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_online', 'is_active', 'is_verified', 'is_staff',
                  'has_verified_email', 'full_address',
                  'email_verified_at', 'created_at', 'updated_at']

    def get_has_verified_email(self, obj: User) -> bool:
        return obj.is_verified

    def get_full_address(self, obj: User):
        return f"{obj.address}, {obj.city}, {obj.country.name}"


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
