from django.conf import settings
from django.db import models
from django.db.models import Q


class FriendshipManager(models.Manager):
    def friends(self, user):
        friendships = self.get_queryset().select_related('user1', 'user2').filter(Q(user1=user) | Q(user2=user))
        return [
            friendship.user1 if friendship.user2 == user else friendship.user2
            for friendship in friendships
        ]


class Friendship(models.Model):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    STATUSES = (
      (PENDING, PENDING),
      (ACCEPTED, ACCEPTED),
      (REJECTED, REJECTED),
    )
    user1 = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='user1_friendships'
    )
    user2 = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='user2_friendships'
    )
    status = models.CharField(max_length=8, choices=STATUSES, default=PENDING)
