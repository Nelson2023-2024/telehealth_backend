from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    # Token management
    path(
        "token/validate/",
        views.validate_token,
        name="validate_token",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "token/refresh/custom", views.token_refresh_custom, name="token_refresh_custom"
    ),
    # User
    path(
        "profile/",
        views.user_profile,
        name="user_profile",
    ),
    # Email verification
    path(
        "verify-email/",
        views.verify_email,
        name="verify_email",
    ),
    path(
        "resend-verification-email/",
        views.resend_verification_email,
        name="resend_verification_email",
    ),
    path(
        "send-verification-email/",
        views.send_verification_email_authenticated,
        name="send_verification_email_authenticated",
    ),
]
