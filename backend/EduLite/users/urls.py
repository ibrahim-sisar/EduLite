# backend/users/urls.py

from django.urls import path
from . import views 

urlpatterns = [
    # User URLs
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserRetrieveView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', views.UserUpdateDeleteView.as_view(), name='user-update'),
    path('users/search/', views.UserSearchView.as_view(), name='user-search'),
    
    # User Registration URL
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    
    # Group URLs
    path('groups/', views.GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', views.GroupRetrieveUpdateDestroyView.as_view(), name='group-detail'),

    # Profile URLs
    path('users/<int:pk>/profile/', views.UserProfileRetrieveUpdateView.as_view(), name='userprofile-detail'),

    # Friend Request URLs
    path('friend-requests/<int:request_pk>/accept/', views.AcceptFriendRequestView.as_view(), name='friend-request-accept'),
    path('friend-requests/<int:request_pk>/decline/', views.DeclineFriendRequestView.as_view(), name='friend-request-decline'),
    path('friend-requests/pending/', views.PendingFriendRequestListView.as_view(), name='friend-request-pending-list'),
    path('friend-requests/send/', views.SendFriendRequestView.as_view(), name='friend-request-send'), 
]