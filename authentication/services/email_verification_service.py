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


class EmailVerificationService:
    pass
