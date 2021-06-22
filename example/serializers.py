from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Friendship

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username',)
        read_only_fields = fields


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ('id', 'user1', 'user2', 'status',)
        read_only_fields = ('id',)
