from django.urls import path
from .views import (
    UserCreateView,
    ProfileView,
    login_page,
    profile_page,
)

urlpatterns = [
    # API
    path('register/', UserCreateView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # HTML Pages
    path('login-page/', login_page, name='login_page'),
    path('profile-page/', profile_page, name='profile_page'),
]