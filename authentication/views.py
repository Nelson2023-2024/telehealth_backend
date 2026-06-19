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
    UserSerilizer,
    ResendVerificationSerializer,
    EmailVerificationSerializer,
)
from .services.auth_service import AuthenticationOrchestrator
from .services.email_verification_service import EmailVerificationOrchestrator

User = get_user_model()

logger = logging.getLogger(__name__)

# Create your views here.


@api_view(["POST"])
@permission_classes([AllowAny])  # Anyone access this endpoint
def register(request: Request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user, error = AuthenticationOrchestrator.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            role=serializer.validated_data.get(
                ["role", "patient"]
            ),  # default role: patient if not provided
        )

        if user:
            try:
                EmailVerificationOrchestrator.send_verification_email(user)
            except Exception as e:
                pass

        auth_data, auth_error = AuthenticationOrchestrator.authenticate_user(
            email = serializer.validated_data["email"],
            password= serializer.validated_data["password"],
        )

        if auth_data:

