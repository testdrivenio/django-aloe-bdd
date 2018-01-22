from django.urls import path

from example.views import FriendsView, FriendshipsView

urlpatterns = [
    path('friends/', FriendsView.as_view(), name='friends'),
    path('friendships/', FriendshipsView.as_view(), name='friendships'),
]
