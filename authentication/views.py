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
from base.services.services import UserService

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


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request):
    try:
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return ResponseProvider.validation_error(serializer.errors)

        auth_data, auth_error = AuthenticationOrchestrator.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        # Step 3 — handle failed authentication
        if not auth_data:
            return ResponseProvider.unauthorized(
                error=auth_error or "Invalid email or password"
            )

        AuthenticationOrchestrator.update_user_status(auth_data["user"], is_online=True)

        return ResponseProvider.success(
            message="Login successful",
            data={
                "user": UserSerializer(auth_data["user"]).data,
                "access_token": auth_data["access_token"],
                "refresh_token": auth_data["refresh_token"],
            },
        )
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request: Request):
    refresh_token = request.data.get("refresh_token")

    # Step 1 — blacklist refresh token if provided
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, InvalidToken) as e:
            logger.warning(f"Logout token issue for {request.user.email}: {str(e)}")

    # Step 2 — update user status
    AuthenticationOrchestrator.update_user_status(request.user, is_online=False)

    return ResponseProvider.success(message="Logged out successfully")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def validate_token(request: Request):
    try:
        user = request.user
        AuthenticationOrchestrator.update_user_status(user, is_online=True)

        return ResponseProvider.success(
            message="Token is valid",
            data={
                "user": UserSerializer(user).data,
            },
        )
    except Exception as ex:
        return ResponseProvider.unauthorized(
            message="Token validation failed", error=str(ex)
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request: Request):
    return ResponseProvider.success(data={"user": UserSerializer(request.user).data})


@api_view(["POST"])
@permission_classes([AllowAny])
def token_refresh_custom(request: Request):
    try:
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return ResponseProvider.bad_request(error="Refresh token is required")

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            user_id = refresh.payload.get("user_id")

            user = UserService().get(id=user_id)

            AuthenticationOrchestrator.update_user_status(user, is_online=True)

            return ResponseProvider.success(
                data={"access": access_token, "user": UserSerializer(user).data}
            )
        except (TokenError, InvalidToken, User.DoesNotExist) as ex:
            return ResponseProvider.unauthorized(
                error=str(ex), message="Invalid refresh token"
            )
    except Exception as ex:
        return ResponseProvider.server_error(
            error=str(ex), message="Token refresh failed"
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request: Request):
    try:
        serializer = EmailVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return ResponseProvider.validation_error(serializer.errors)

        token = serializer.validated_data["token"]

        user, error = EmailVerificationOrchestrator.verify_email_token(token)

        if not user:
            return ResponseProvider.bad_request(error=error)

        return ResponseProvider.success(
            message="Email verified successfully",
            data={
                "user": UserSerializer(user).data,
            },
        )

    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification_email(request):
    try:
        serializer = ResendVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return ResponseProvider.validation_error(serializer.errors)

        email = serializer.validated_data["email"]

        user = UserService().get(email=email)

        if user is None:
            return ResponseProvider.not_found(error="User with this email not found")

        success, message = EmailVerificationOrchestrator.resend_verification_email(user)

        if success:
            return ResponseProvider.success(message=message, data={"email_sent": True})
        return ResponseProvider.bad_request(
            error=message,
            data={"email_sent": False}
        )
    except User.DoesNotExist:
        return ResponseProvider.not_found(error="User with this email not found")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_verification_email_authenticated(request: Request):
    user = request.user

    if user.is_verified:
        return ResponseProvider.bad_request(
            error="Email is already verified",
            data={"email_sent": False}
        )

    success, message = EmailVerificationOrchestrator.resend_verification_email(user)
    if success:
        return ResponseProvider.success(message=message, data={"email_sent": True})
    return ResponseProvider.bad_request(error=message, data={"email_sent": False})
