"""Authentication API views."""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.core.responses import success_response, validation_error_response
from apps.identity.authentication.exceptions import (
    AuthenticationError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    TokenBlacklistError,
)
from apps.identity.authentication.serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    MeSerializer,
    RegisterSerializer,
)
from apps.identity.authentication.services import (
    AuthenticationService,
    LoginService,
    RegistrationService,
)


class RegisterView(GenericAPIView):
    """Register a new user and provision their personal workspace."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        try:
            result = RegistrationService().register(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                display_name=serializer.validated_data.get("display_name"),
            )
        except EmailAlreadyExistsError as exc:
            return validation_error_response({"email": [exc.message]})
        except AuthenticationError as exc:
            return validation_error_response({"non_field_errors": [exc.message]})

        data = AuthResponseSerializer(
            {
                "user": result.user,
                "profile": result.profile,
                "organizations": [result.organization],
                "membership": result.membership,
                "current_organization": result.organization,
                "tokens": result.tokens,
            }
        ).data

        return success_response(
            data=data,
            message="Registration successful.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(GenericAPIView):
    """Authenticate a user with email and password."""

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        try:
            result = LoginService().login(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except InvalidCredentialsError as exc:
            return validation_error_response({"non_field_errors": [exc.message]})
        except InactiveUserError as exc:
            return validation_error_response({"non_field_errors": [exc.message]})

        data = AuthResponseSerializer(
            {
                "user": result.user,
                "profile": result.profile,
                "organizations": result.organizations,
                "membership": result.membership,
                "current_organization": result.current_organization,
                "tokens": result.tokens,
            }
        ).data

        return success_response(
            data=data,
            message="Login successful.",
        )


class LogoutView(GenericAPIView):
    """Blacklist the refresh token to end the session."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        try:
            AuthenticationService().logout(serializer.validated_data["refresh"])
        except TokenBlacklistError as exc:
            return validation_error_response({"refresh": [exc.message]})

        return success_response(message="Logout successful.")


class MeView(APIView):
    """Return the authenticated user's full context."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        result = AuthenticationService().get_me_context(request.user)

        data = MeSerializer(
            {
                "user": result.user,
                "profile": result.profile,
                "organizations": result.organizations,
                "membership": result.membership,
                "role": result.role,
                "permissions": result.permissions,
                "current_organization": result.current_organization,
            }
        ).data

        return success_response(
            data=data,
            message="User profile retrieved.",
        )


class TokenRefreshView(TokenRefreshView):
    """
    Refresh JWT access token.

    Wraps SimpleJWT's TokenRefreshView to preserve the standard response
    envelope while delegating token validation to the library.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code >= 400:
            return validation_error_response(response.data)

        return success_response(
            data=response.data,
            message="Token refreshed.",
        )
