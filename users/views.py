from .models import FriendRequest
from .serializers import FriendRequestSerializer
from rest_framework import generics, permissions
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response


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