from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from .models import Friendship


class FriendsView(View):
    def get(self, request):
        # friends = Friendship.objects.friends(request.user)
        friendships = Friendship.objects.select_related('user1', 'user2').filter(
            Q(user1=request.user) |
            Q(user2=request.user)
        )
        friends = [f.user1 if f.user2 == request.user else f.user2 for f in friendships]
        return JsonResponse([{
            'id': friend.id,
            'email': friend.email,
            'username': friend.username,
        } for friend in friends], safe=False)


class FriendshipsView(View):
    def post(self, request, *args, **kwargs):
        user1 = User.objects.get(id=request.POST['user1'])
        user2 = User.objects.get(id=request.POST['user2'])

        # Confirm the friendship is not with yourself.
        if user1 == user2:
            return JsonResponse(
                data={'detail': 'You cannot create a friendship with yourself.'}
            )

        # Confirm the friendship does not exist.
        has_friendship = Friendship.objects.filter(
            Q(user1=user1, user2=user2) |
            Q(user1=user2, user2=user1)
        ).exists()

        if has_friendship:
            return JsonResponse(
                data={'detail': 'You cannot create a new friendship with an existing friend.'}
            )

        friendship = Friendship.objects.create(user1=user1, user2=user2)

        return JsonResponse({
            'id': friendship.id,
            'user1': friendship.user1.id,
            'user2': friendship.user2.id,
        })
