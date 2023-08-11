from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from user.v1 import views

urlpatterns = [
    # path('list-user/', views.UserApiView.as_view()),
    path('register/', views.UserView.as_view(), name="Registration"),
    path('verify/<uidb64>/<token>', views.VerifyView.as_view(), name="Email_Verification"),
    path('verify/resend/', views.ResendEmailView.as_view(), name="Resend Verification Link"),

    path('restore/', views.RestoreView.as_view(), name='Retrive Account'),

    path('reset_password', views.PasswordResetView.as_view(), name="Reset password"),
    path('reset_password/<uidb64>/<token>', views.VerifyPasswordResetLink.as_view(), name='set new password'),
    
    path('profile/', views.UserProfileApiView.as_view(), name='Profile'),
    path('update_password/', views.UpdatePasswordView.as_view(), name="Update_Password"),
    
    path('login/', views.LoginView.as_view(), name='User Login'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='Token_Refresh'),
    
    path('logout/', views.LogoutView.as_view(), name="Logout")
]