from .models import FriendRequest
from .serializers import FriendRequestSerializer
from rest_framework import generics, permissions
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import serializers
from .models import Message
from .serializers import MessageSerializer

class UserCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
def login_page(request):
    return render(request, "login.html")

def chat_page(request):
    return render(request, "chat.html")

def profile_page(request):
    return render(request, "profile.html")

def dashboard_page(request):
    return render(request, "dashboard.html")

class FriendRequestCreateView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")

        receiver = User.objects.get(id=receiver_id)

        # Duplicate request check
        if FriendRequest.objects.filter(
            sender=self.request.user,
            receiver=receiver,
            status="pending"
        ).exists():
            raise serializers.ValidationError("Friend request already sent.")

        serializer.save(
            sender=self.request.user,
            receiver=receiver
        )
class FriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            receiver=self.request.user,
            status="pending"
        )
class FriendRequestAcceptView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            receiver=self.request.user,
            status="pending"
        )

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()

        friend_request.status = "accepted"
        friend_request.save()

        serializer = self.get_serializer(friend_request)

        return Response(serializer.data)
class FriendsListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user),
            status="accepted"
        )
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")

        receiver = User.objects.get(id=receiver_id)

        serializer.save(
            sender=self.request.user,
            receiver=receiver
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user_id = self.kwargs["user_id"]

        return Message.objects.filter(
            Q(sender=self.request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=self.request.user)
        ).order_by("created_at")