from django.urls import path
from .views import UserCreateView, ProfileView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
]