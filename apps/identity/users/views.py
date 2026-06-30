from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.users.models import User
from apps.identity.users.serializers import UserSerializer


class IdentityStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "service": "identity",
                "status": "ok",
                "user_model": "users.User",
            }
        )


class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(deleted_at__isnull=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
