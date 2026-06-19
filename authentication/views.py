from django.core.serializers import serialize
from django.shortcuts import render

from rest_framework import status

from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request

from rest_framework.response import Response
import logging

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    UserSerializer,
    ResendVerificationSerializer,
    EmailVerificationSerializer,
)
from .services.auth_service import AuthenticationOrchestrator
from .services.email_verification_service import EmailVerificationOrchestrator
from base.utils.response_provider import ResponseProvider

User = get_user_model()

logger = logging.getLogger(__name__)


# Create your views here.
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request: Request):
    """User registration endpoint"""
    try:
        # Step 1 — validate incoming data against the serializer rules
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseProvider.validation_error(serializer.errors)

        # Step 2 — call the orchestrator to create the user
        user, error = AuthenticationOrchestrator.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            role=serializer.validated_data.get("role", "patient"),
        )

        # Step 3 — if user creation failed, stop here
        if error:
            return ResponseProvider.bad_request(error=error)

        # Step 4 — send the verification email (failure here shouldn't block registration)
        try:
            EmailVerificationOrchestrator.send_verification_email(user)
        except Exception as e:
            logger.exception(f"Failed to send verification email to {user.email}: {e}")

        # Step 5 — log the user in immediately after registering
        auth_data, auth_error = AuthenticationOrchestrator.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        # Step 6 — if login fails right after registration, something's wrong
        if not auth_data:
            return ResponseProvider.server_error(
                error=f"Registration successful but login failed: {auth_error}"
            )

        # Step 7 — mark the user online
        AuthenticationOrchestrator.update_user_status(auth_data["user"], is_online=True)

        # Step 8 — return success with tokens
        return ResponseProvider.created(
            message=(
                "User registered successfully. "
                "Please check your email to verify your account."
            ),
            data={
                "user": UserSerializer(auth_data["user"]).data,
                "access_token": auth_data["access_token"],
                "refresh_token": auth_data["refresh_token"],
            },
        )
    except Exception as e:
        return ResponseProvider.handle_exception(e)
