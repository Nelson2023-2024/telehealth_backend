from rest_framework import serializers
from django.contrib.auth import get_user_model
from base.services.services import UserService
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registrtion serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return UserService().create_user(**validated_data)


class UserSerilizer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    has_verified_email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_online', 'is_active', 'is_verified', 'is_staff',
                  'has_verified_email'
                  'email_verified_at', 'created_at', 'updated_at']

    def get_has_verified_email(self, obj):
        return obj.is_verified


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
