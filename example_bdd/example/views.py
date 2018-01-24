import json

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Friendship


class FriendsView(View):
    def get(self, request, *args, **kwargs):
        # Get all friendships that involve the logged-in user.
        friendships = Friendship.objects.select_related('user1', 'user2').filter(
            Q(user1=request.user) |
            Q(user2=request.user),
            status=Friendship.ACCEPTED
        )

        # Get a list of friends.
        friends = [
            friendship.user1
            if friendship.user2 == request.user
            else friendship.user2
            for friendship in friendships
        ]

        # Return a JSON-serialized list of friend data.
        return JsonResponse([{
            'id': friend.id,
            'email': friend.email,
            'username': friend.username,
        } for friend in friends], safe=False)


class FriendshipRequestsView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        user = get_object_or_404(User, username=username)

        # Confirm the friendship is not with yourself.
        if request.user == user:
            return JsonResponse(
                data={'detail': 'You cannot create a friendship with yourself.'}
            )

        # Confirm the friendship does not exist.
        has_friendship = Friendship.objects.filter(
            Q(user1=request.user, user2=user) |
            Q(user1=user, user2=request.user)
        ).exists()

        if has_friendship:
            return JsonResponse(
                data={'detail': 'You cannot create a new friendship with an existing friend.'}
            )

        # Create a new friendship between the users.
        friendship = Friendship.objects.create(user1=request.user, user2=user)

        return JsonResponse({
            'id': friendship.id,
            'user1': friendship.user1_id,
            'user2': friendship.user2_id,
            'status': friendship.status,
        })

    def put(self, request, *args, **kwargs):
        friendship = get_object_or_404(Friendship, pk=kwargs.get('pk'))
        for key, value in json.loads(request.body).items():
            setattr(friendship, key, value)
        friendship.save()

        return JsonResponse({
            'id': friendship.id,
            'user1': friendship.user1_id,
            'user2': friendship.user2_id,
            'status': friendship.status,
        })
