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
from .models import Like, Match

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

    try:
        liked_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=404
        )

    # Create Like
    like, created = Like.objects.get_or_create(
        liker=request.user,
        liked_user=liked_user
    )

    # Already liked
    if not created:
        return Response({
            "message": "Already liked",
            "matched": False
        })

    # Check whether the other person already liked us
    mutual_like = Like.objects.filter(
        liker=liked_user,
        liked_user=request.user
    ).exists()

    # Mutual like = MATCH
    if mutual_like:

        user1, user2 = sorted(
            [request.user, liked_user],
            key=lambda user: user.id
        )

        match, match_created = Match.objects.get_or_create(
            user1=user1,
            user2=user2
        )

        return Response({
            "message": "❤️ It's a Match!",
            "matched": True,
            "match_id": match.id,
            "user": liked_user.username
        }, status=201)

    return Response({
        "message": "❤️ Like sent successfully",
        "matched": False,
        "user": liked_user.username
    }, status=201)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def likes_received(request):

    likes = Like.objects.filter(
        liked_user=request.user
    ).select_related("liker")

    result = []

    for like in likes:

        already_liked_back = Like.objects.filter(
            liker=request.user,
            liked_user=like.liker
        ).exists()

        result.append({
            "like_id": like.id,
            "user": {
                "id": like.liker.id,
                "username": like.liker.username,
                "city": like.liker.city,
                "profile_picture": (
                    like.liker.profile_picture.url
                    if like.liker.profile_picture
                    else None
                )
            },
            "liked_back": already_liked_back
        })

    return Response(result)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_matches(request):

    matches = Match.objects.filter(
        Q(user1=request.user) |
        Q(user2=request.user)
    ).select_related("user1", "user2")

    result = []

    for match in matches:

        if match.user1.id == request.user.id:
            other_user = match.user2
        else:
            other_user = match.user1

        result.append({
            "match_id": match.id,
            "user": {
                "id": other_user.id,
                "username": other_user.username,
                "city": other_user.city,
                "profile_picture": (
                    other_user.profile_picture.url
                    if other_user.profile_picture
                    else None
                )
            },
            "matched_at": match.created_at
        })

    return Response(result)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unmatch_user(request, match_id):

    try:
        match = Match.objects.get(
            id=match_id
        )
    except Match.DoesNotExist:
        return Response(
            {"error": "Match not found"},
            status=404
        )

    if request.user.id not in [
        match.user1.id,
        match.user2.id
    ]:
        return Response(
            {"error": "You are not part of this match"},
            status=403
        )

    other_user = (
        match.user2
        if match.user1.id == request.user.id
        else match.user1
    )

    match.delete()

    return Response({
        "message": f"Unmatched with {other_user.username}"
    })