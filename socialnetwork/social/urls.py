from concurrent.futures import thread
from unicodedata import name
from django.urls import path
from .views import *

urlpatterns = [
    path('',PostListView.as_view(),name='post-list'),
    path('post/<int:pk>',PostDetailView.as_view(),name='post-detail'),
    path('post/edit/<int:pk>',PostEditView.as_view(),name='post-edit'),
    path('post/delete/<int:pk>',PostDeleteView.as_view(),name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/',CommentDeleteView.as_view(),name='comment-delete'),
    path('post/<int:pk>/like',AddLike.as_view(),name='like'),
    path('post/<int:pk>/dislike',Dislike.as_view(),name='dislike'),
    path('profile/<int:pk>/',ProfileView.as_view(),name='profile'),
    path('profile/edit/<int:pk>/',ProfileEditView.as_view(),name='profile-edit'),
    path('profile/<int:pk>/friends/add',AddFriend.as_view(),name='add-friends'),
    path('profile/<int:pk>/friends/remove',RemoveFriend.as_view(),name='remove-friends'),
    path('profile/<int:pk>/friends/',ListFriends.as_view(),name='list-friends'),
    path('search/',UserSearch.as_view(),name="profile-search"),
    path('inbox/',ListThreads.as_view(),name='inbox'),
    path('inbox/create-thread/',CreateThread.as_view(),name='create-thread'),
    path('inbox/<int:pk>/',ThreadView.as_view(),name='thread'),
    path('inbox/<int:pk>/create-message/',CreateMessage.as_view(),name='create-message')

]