"""Global DRF exception handler for consistent API error responses."""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.responses import error_response


def custom_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response | None:
    """Map DRF exceptions to the standard error envelope."""
    response = exception_handler(exc, context)

    if response is None:
        return None

    if isinstance(exc, ValidationError):
        return validation_error_response_from_exc(exc, response)

    message = _extract_message(response.data)
    errors = response.data if isinstance(response.data, dict) else {"detail": response.data}

    return error_response(
        message=message,
        errors=errors,
        status_code=response.status_code,
    )


def validation_error_response_from_exc(
    exc: ValidationError,
    response: Response,
) -> Response:
    """Normalize DRF ValidationError payloads."""
    errors = exc.detail
    if not isinstance(errors, dict):
        errors = {"non_field_errors": errors}

    return error_response(
        message="Validation failed.",
        errors=errors,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def _extract_message(data: Any) -> str:
    if isinstance(data, dict):
        if "detail" in data:
            detail = data["detail"]
            if isinstance(detail, list):
                return str(detail[0])
            return str(detail)
    return "Request failed."
