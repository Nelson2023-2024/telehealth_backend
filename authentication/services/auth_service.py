import email

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from base.services.services import UserService, ConsultantProfileService
from ..models import User, EmailVerificationToken
from consoltants.models import ConsultantProfile
import uuid
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class AuthenticationOrchestrator:
    @staticmethod
    def register_user(email, password, first_name, last_name, role="patient"):
        try:
            # Check if user exists
            existing = UserService().filter(email=email)
            if existing is None:
                # filter() returned None — means a DB error occurred
                logger.error(f"[Register] DB error checking existing user: {email}")
                return None, "Something went wrong, please try again"

            if existing.exists():
                return None, "User with this email already exists"

            # Create user
            user = UserService().create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )

            if user is None:
                # create_user() returned None — means creation failed
                logger.error(f"[Register] Failed to create user: {email}")
                return None, "Failed to create account, please try again"

            # Create consultant profile if needed
            if role == "consultant":
                profile = ConsultantProfileService().create(user=user)
                if profile is None:
                    logger.error(
                        f"[Register] Failed to create consultant profile for: {email}"
                    )
                    # User was created but profile failed
                    # You may want to delete the user here or handle this case
                    return None, "Failed to create consultant profile"

            logger.info(
                f"[Register] User registered successfully: {email} with role {role}"
            )
            return user, None

        except Exception as e:
            logger.exception(f"[Register] Unexpected error for {email}: {e}")
            return None, str(e)

    @staticmethod
    def authenticate_user(email, password):
        try:
            user = UserService().get(email=email)
            if user is None:
                return None, "Invalid email or password"  # vague on purpose — security

            if not user.is_active and user.state__code != "Active":
                return None, "Account is disabled, contact support"

            # Verify password
            user = authenticate(email=email, password=password)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            print(refresh)

            tokens = {
                "user": user,
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
            }

            # Update last seen
            user.last_seen = timezone.now()

            user.save(update_fields=["is_online", "last_seen"])

            logger.info(f"[Login] User logged in: {email}")
            return tokens, None

        except Exception as e:
            logger.exception(f"[Login] Unexpected error for {email}: {e}")
            return None, f"An unexpected error occurred: {e}"

    @staticmethod
    def update_user_status(user: User, is_online = True):
        try:
            user.
        except Exception as e:
            pass
