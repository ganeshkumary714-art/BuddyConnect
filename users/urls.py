from django.urls import path
from .views import (
    UserCreateView,
    ProfileView,
    login_page,
    profile_page,
    dashboard_page,
    FriendRequestCreateView,
    FriendRequestListView,
    FriendRequestAcceptView,
)

urlpatterns = [
    # API
    path('register/', UserCreateView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # HTML Pages
    path('login-page/', login_page, name='login_page'),
    path('profile-page/', profile_page, name='profile_page'),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("friend-request/", FriendRequestCreateView.as_view(), name="friend_request"),
    path("friend-requests/", FriendRequestListView.as_view(), name="friend_requests"),
    path("friend-request/<int:pk>/accept/", FriendRequestAcceptView.as_view(), name="friend_request_accept"
),
]