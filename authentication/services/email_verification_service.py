from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone

from base.services.services import (
    UserService,
    ConsultantProfileService,
    EmailVerificationTokenService,
)
from ..models import User, EmailVerificationToken

import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class EmailVerificationOrchestrator:
    @staticmethod
    def send_verification_email(user):
        try:
            existing_token = EmailVerificationTokenService().filter(user=user, is_used=False)

            if existing_token is not None:
                existing_token.update(is_used=True)

            # Create a new token
            verification_token = EmailVerificationTokenService().create(user=user)
            if verification_token is None:
                logger.error(f"Failed to create verification token for {user.email}")
                return False

            subject = (
                f'Verify your Email - {getattr(settings, "APP_NAME", "Telehealth App")}'
            )
            print(subject)

            verification_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token.token}"

            html_message = render_to_string(
                "emails/email_verification.html",
                {
                    "user": user,
                    "verification_url": verification_url,
                    "app_name": getattr(settings, "APP_NAME", "Telehealth App"),
                },
            )

            plain_message = f"""
            Hi {user.first_name},
            Thank you for signing up for {getattr(settings, 'APP_NAME', 'Telehealth App')}!
            Please verify your email address by clicking the link below:
            {verification_url}
            This link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.

            Best regards,
            The Telehealth Team
            """
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@telehealth.com"
                ),
                recipient_list=[user.email],
                fail_silently=False,
            )

            logger.info(f"Verification email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"An error occurred sending verification email to {user}: {e}")
