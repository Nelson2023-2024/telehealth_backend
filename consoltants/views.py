from django.core.serializers import serialize
from django.shortcuts import render

from rest_framework import status

from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
import logging

from django.contrib.auth import get_user_model

from base.utils.response_provider import ResponseProvider
from .serializers import (
    ConsultantAvailabilitySerializer,
    ConsultantProfileCreateSerializer,
    ConsultantProfileDetailSerializer,
    ConsultantProfileListSerializer,
    ConsultantProfileUpdateSerializer,
    SpecialitySerializer,
)

from base.services.services import (
    SpecialityService,
    ConsultantProfileService,
    ConsultantAvailabilityService,
)

# Create your views here.
