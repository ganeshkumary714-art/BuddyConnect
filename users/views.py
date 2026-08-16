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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Like

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

def discover_page(request):
    return render(request, "discover.html")

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

        Message.objects.filter(
            sender_id=user_id,
            receiver=self.request.user,
            is_read=False
        ).update(is_read=True)

        return Message.objects.filter(
            Q(sender=self.request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=self.request.user)
        ).order_by("created_at")
    
from rest_framework.views import APIView
from rest_framework.response import Response

class UnreadMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        unread = Message.objects.filter(
            receiver=request.user,
            is_read=False
        )

        result = {}

        for msg in unread:

            sender_id = msg.sender.id

            if sender_id not in result:
                result[sender_id] = 0

            result[sender_id] += 1

        return Response(result)
    
from .models import Message

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, user_id):

    Message.objects.filter(
        sender_id=user_id,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return Response({
        "message": "Messages marked as read"
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_user(request, user_id):

    if request.user.id == user_id:
        return Response(
            {"error": "You cannot like yourself"},
            status=400
        )

    liked_user = User.objects.get(id=user_id)

    like, created = Like.objects.get_or_create(
        liker=request.user,
        liked_user=liked_user
    )

    if not created:
        return Response({
            "message": "Already liked"
        })

    return Response({
        "message": "User liked successfully",
        "liked_user": liked_user.username
    }, status=201)