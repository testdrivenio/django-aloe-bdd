from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from .models import Friendship
from .serializers import UserSerializer, FriendshipSerializer


class FriendsView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return Friendship.objects.friends(self.request.user)


class FriendshipRequestsView(ModelViewSet):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        return Friendship.objects.friendships(self.request.user)
