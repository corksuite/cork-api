from django.urls import path

from apps.identity.users.views import IdentityStatusView, UserListView

app_name = "identity_users"

urlpatterns = [
    path("status/", IdentityStatusView.as_view(), name="status"),
    path("users/", UserListView.as_view(), name="user-list"),
]
