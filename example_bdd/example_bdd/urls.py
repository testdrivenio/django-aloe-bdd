from django.urls import path

from example.views import FriendsView, FriendshipRequestsView

urlpatterns = [
    path('friends/', FriendsView.as_view()),
    path('friendship-requests/', FriendshipRequestsView.as_view({'post': 'create'})),
    path('friendship-requests/<int:pk>/', FriendshipRequestsView.as_view({'put': 'partial_update'}))
]
