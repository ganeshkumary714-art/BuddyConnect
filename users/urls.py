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
    FriendsListView,
    UserListView,
    MessageCreateView,
    MessageListView,
    chat_page,
    UnreadMessageView,
    discover_page,
    like_user,
    likes_received,
    my_matches,
    unmatch_user,
)

urlpatterns = [

    # API
    path("register/", UserCreateView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),

    # HTML Pages
    path("login-page/", login_page, name="login_page"),
    path("profile-page/", profile_page, name="profile_page"),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("chat/", chat_page, name="chat"),
    path("discover/", discover_page, name="discover"),

    # Friend Request
    path("friend-request/", FriendRequestCreateView.as_view(), name="friend_request"),
    path("friend-requests/", FriendRequestListView.as_view(), name="friend_requests"),
    path("friend-request/<int:pk>/accept/", FriendRequestAcceptView.as_view(), name="friend_request_accept"),

    # Friends
    path("friends/", FriendsListView.as_view(), name="friends"),
    path("users/", UserListView.as_view(), name="users"),

    # Chat
    path("messages/", MessageCreateView.as_view(), name="send_message"),
    path("messages/<int:user_id>/", MessageListView.as_view(), name="chat_history"),
    path("unread-messages/", UnreadMessageView.as_view(), name="unread_messages"),

    #like
    path("like/<int:user_id>/", like_user, name="like-user"),
    path("likes-received/", likes_received, name="likes-received"),
    path("matches/", my_matches, name="my-matches"),
    path("unmatch/<int:match_id>/", unmatch_user, name="unmatch-user"),
]