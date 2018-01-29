from django.conf import settings
from django.db import models
from django.db.models import Q


class FriendshipManager(models.Manager):
    def friendships(self, user):
        """Get all friendships that involve the specified user."""
        return self.get_queryset().select_related(
            'user1', 'user2'
        ).filter(
            Q(user1=user) |
            Q(user2=user)
        )

    def friends(self, user):
        """Get all users that are friends with the specified user."""
        friendships = self.friendships(user).filter(status=Friendship.ACCEPTED)

        def other_user(friendship):
            if friendship.user1 == user:
                return friendship.user2
            return friendship.user1

        return map(other_user, friendships)


class Friendship(models.Model):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    STATUSES = (
      (PENDING, PENDING),
      (ACCEPTED, ACCEPTED),
      (REJECTED, REJECTED),
    )
    objects = FriendshipManager()
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
