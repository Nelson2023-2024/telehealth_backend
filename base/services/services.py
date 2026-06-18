# -*- coding: utf-8 -*-
"""
All model services for the telehealth system.
Every model has a corresponding service that inherits from ServiceBase.
"""

from base.services.servicebase import ServiceBase
import logging

lgr = logging.getLogger(__name__)

# Base models
from base.models import State, Country

# Authentication models
from authentication.models import User, EmailVerificationToken, Role, Permission

# Patient models
from patients.models import PatientProfile, PatientMedicalHistory

# Consultant models
from consoltants.models import (
    Speciality,
    ConsultantProfile,
    ConsultantReview,
    ConsultantAvailability,
)

# ─── Base Services ────────────────────────────────────────────────


class StateService(ServiceBase[State]):
    """Handles CRUD operations for the State model."""

    manager = State.objects


class CountryService(ServiceBase[Country]):
    """Handles CRUD operations for the Country model."""

    manager = Country.objects


# ─── Authentication Services ──────────────────────────────────────


class UserService(ServiceBase[User]):
    """Handles CRUD operations for the User model."""

    manager = User.objects

    def create_user(self, **kwargs):
        """
        Creates a user with a hashed password.
        Uses Django's create_user() which hashes the password properly.
        """
        try:
            return self.manager.create_user(**kwargs)
        except Exception as e:
            lgr.exception(
                "[User] CREATE_USER failed. Data: %s | Error: %s", kwargs, str(e)
            )
            return None

    def create_superuser(self, **kwargs):
        """Creates a superuser with a hashed password and admin privileges."""
        try:
            return self.manager.create_superuser(**kwargs)
        except Exception as e:
            lgr.exception(
                "[User] CREATE_SUPERUSER failed. Data: %s | Error: %s", kwargs, str(e)
            )
            return None


class RoleService(ServiceBase[Role]):
    """Handles CRUD operations for the Role model."""

    manager = Role.objects


class PermissionService(ServiceBase[Permission]):
    """Handles CRUD operations for the Permission model."""

    manager = Permission.objects


class EmailVerificationTokenService(ServiceBase[EmailVerificationToken]):
    """Handles CRUD operations for the EmailVerificationToken model."""

    manager = EmailVerificationToken.objects


# ─── Patient Services ─────────────────────────────────────────────


class PatientProfileService(ServiceBase[PatientProfile]):
    """Handles CRUD operations for the PatientProfile model."""

    manager = PatientProfile.objects


class PatientMedicalHistoryService(ServiceBase[PatientMedicalHistory]):
    """Handles CRUD operations for the PatientMedicalHistory model."""

    manager = PatientMedicalHistory.objects


# ─── Consultant Services ──────────────────────────────────────────


class SpecialityService(ServiceBase[Speciality]):
    """Handles CRUD operations for the Speciality model."""

    manager = Speciality.objects


class ConsultantProfileService(ServiceBase[ConsultantProfile]):
    """Handles CRUD operations for the ConsultantProfile model."""

    manager = ConsultantProfile.objects


class ConsultantReviewService(ServiceBase[ConsultantReview]):
    """Handles CRUD operations for the ConsultantReview model."""

    manager = ConsultantReview.objects


class ConsultantAvailabilityService(ServiceBase[ConsultantAvailability]):
    """Handles CRUD operations for the ConsultantAvailability model."""

    manager = ConsultantAvailability.objects
