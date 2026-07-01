"""Standard API response envelope helpers."""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response


def success_response(
    data: Any = None,
    message: str = "Success.",
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """Return a consistent success envelope."""
    payload: dict[str, Any] = {
        "success": True,
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status_code)


def error_response(
    message: str = "An error occurred.",
    errors: dict[str, Any] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """Return a consistent error envelope."""
    payload: dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)


def validation_error_response(errors: dict[str, Any]) -> Response:
    """Return a validation error envelope."""
    return error_response(
        message="Validation failed.",
        errors=errors,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
