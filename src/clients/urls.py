from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login")),

    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    
    path("change-password/", 
         auth_views.PasswordChangeView.as_view(
             template_name="accounts/auth.html", 
             success_url=reverse_lazy("change_password_done")
        ),
        name="change_password"
    ),
    
    path("change-password/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="change_password_done"),
    
    path("forgot-password/", 
         auth_views.PasswordResetView.as_view(template_name="accounts/auth.html", success_url=reverse_lazy("password_reset_done")),
         name="password_reset"),

    path("forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password-reset.html"),
        name="password_reset_done"),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="accounts/auth.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/reset-password-complete.html"),
        name="password_reset_complete",
    ),

    path(
        "activate/<int:user_id>/<str:token>/",
        views.AccountActivationView.as_view(),
        name="account_activation"
    ),
]
