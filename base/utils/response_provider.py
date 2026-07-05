import logging
from rest_framework.response import Response
from rest_framework import status as http_status
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db import IntegrityError, OperationalError, DataError

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    NotFound as DRFNotFound,
    Throttled,
    MethodNotAllowed,
)
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger(__name__)


class ResponseProvider:
    """
    Centralized response builder so every endpoint returns a consistent shape:
    {"success": bool, "code": str, "message": str, "data": {...}, "error": "..."}
    """

    @staticmethod
    def _response(
        success: bool, code: str, message: str, status: int, data=None, error=None
    ) -> Response:
        if data is None:
            data = {}
        return Response(
            {
                "success": success,
                "code": code,
                "message": message,
                "data": data,
                "error": error or "",
            },
            status=status,
        )

    @classmethod
    def handle_exception(cls, ex: Exception) -> Response:
        """
        Maps any caught exception to the correct response automatically.
        Usage: except Exception as e: return ResponseProvider.handle_exception(e)
        """
        if isinstance(ex, ValidationError):
            error_message = (
                ", ".join(ex.messages) if hasattr(ex, "messages") else str(ex)
            )
            return cls.bad_request(message="Validation Error", error=error_message)

        elif isinstance(ex, ObjectDoesNotExist):
            return cls.not_found(error=str(ex))

        elif isinstance(ex, PermissionDenied):
            return cls.forbidden(error=str(ex))

        elif isinstance(ex, ValueError):
            return cls.bad_request(message="Bad Request", error=str(ex))

        elif isinstance(ex, TypeError):
            return cls.bad_request(message="Invalid data type provided", error=str(ex))

        elif isinstance(ex, IntegrityError):
            logger.exception(f"[IntegrityError] {ex}")
            return cls.conflict(
                error="A record with this data already exists or a required relation is missing."
            )

        elif isinstance(ex, DataError):
            logger.exception(f"[DataError] {ex}")
            return cls.bad_request(
                message="Data error",
                error="A provided value exceeds the allowed length or range.",
            )

        elif isinstance(ex, OperationalError):
            logger.exception(f"[OperationalError] {ex}")
            return cls.service_unavailable(
                error="A database error occurred. Please try again later."
            )

        # Add these checks in handle_exception()
        elif isinstance(ex, DRFValidationError):
            return cls.bad_request(message="Validation Error", error=ex.detail)

        elif isinstance(ex, AuthenticationFailed):
            return cls.unauthorized(error=str(ex))

        elif isinstance(ex, NotAuthenticated):
            return cls.unauthorized(
                error="Authentication credentials were not provided"
            )

        elif isinstance(ex, Throttled):
            return cls.too_many_requests(
                error=f"Request was throttled. Try again in {ex.wait} seconds"
            )

        elif isinstance(ex, MethodNotAllowed):
            return cls.bad_request(
                code="405.000", message="Method Not Allowed", error=str(ex)
            )

        else:
            logger.exception(f"[UnhandledError] {ex}")
            return cls.server_error(error=str(ex))

    @classmethod
    def success(cls, code="200.000", message="Success", data=None):
        return cls._response(True, code, message, http_status.HTTP_200_OK, data=data)

    @classmethod
    def created(cls, code="201.000", message="Created", data=None):
        return cls._response(
            True, code, message, http_status.HTTP_201_CREATED, data=data
        )

    @classmethod
    def accepted(cls, code="202.000", message="Accepted", data=None):
        return cls._response(
            True, code, message, http_status.HTTP_202_ACCEPTED, data=data
        )

    @classmethod
    def bad_request(cls, code="400.000", message="Bad Request", error=None, data=None):
        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_400_BAD_REQUEST,
            error=error,
            data=data,
        )

    @classmethod
    def unauthorized(
        cls, code="401.000", message="Unauthorized", error=None, data=None
    ):
        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_401_UNAUTHORIZED,
            error=error,
            data=data,
        )

    @classmethod
    def forbidden(cls, code="403.000", message="Forbidden", error=None, data=None):
        return cls._response(
            False, code, message, http_status.HTTP_403_FORBIDDEN, error=error, data=data
        )

    @classmethod
    def not_found(
        cls, code="404.000", message="Resource Not Found", error=None, data=None
    ):
        return cls._response(
            False, code, message, http_status.HTTP_404_NOT_FOUND, error=error, data=data
        )

    @classmethod
    def conflict(cls, code="409.000", message="Conflict", error=None, data=None):
        return cls._response(
            False, code, message, http_status.HTTP_409_CONFLICT, error=error, data=data
        )

    @classmethod
    def too_many_requests(
        cls, code="429.000", message="Rate Limit Exceeded", error=None, data=None
    ):
        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_429_TOO_MANY_REQUESTS,
            error=error,
            data=data,
        )

    @classmethod
    def server_error(
        cls, code="500.000", message="Internal Server Error", error=None, data=None
    ):
        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=error,
            data=data,
        )

    @classmethod
    def not_implemented(
        cls, code="501.000", message="Not Implemented", error=None, data=None
    ):
        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_501_NOT_IMPLEMENTED,
            error=error,
            data=data,
        )

    @classmethod
    def service_unavailable(
        cls, code="503.000", message="Service Unavailable", error=None, data=None
    ):
        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_503_SERVICE_UNAVAILABLE,
            error=error,
            data=data,
        )

    @classmethod
    def no_content(cls, code="204.000", message="No Content"):
        return cls._response(
            True, code, message, http_status.HTTP_204_NO_CONTENT, data=None
        )

    class StandardPagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = "page_size"
        max_page_size = 100

    @classmethod
    def paginated(
        cls,
        queryset,
        request,
        serializer_class,
        code="200.000",
        message="Success",
    ):
        """
        Wraps DRF pagination into the standard response shape.
        """
        paginator = cls.StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(page, many=True)

        return cls._response(
            True,
            code,
            message,
            http_status.HTTP_200_OK,
            data={
                "results": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        )

    @classmethod
    def validation_error(
        cls, serializer_errors, code="400.001", message="Validation failed", data=None
    ):
        """
        Specifically for DRF serializer.errors — flattens them into a readable format.
        """
        flattened = {}
        for field, errors in serializer_errors.items():
            flattened[field] = errors[0] if isinstance(errors, list) else str(errors)

        return cls._response(
            False,
            code,
            message,
            http_status.HTTP_400_BAD_REQUEST,
            error=flattened,
            data=data,
        )
