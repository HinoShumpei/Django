from django.urls import path
from .views import (TweetListView, TweetCreateView, TweetDeleteView, TweetUpdateView, TweetDetailView, register,
                    login_view, logout_view, CommentCreateView)
from . import views

urlpatterns = [
    path('', TweetListView.as_view(), name='tweet_list'),
    path('tweet/', TweetListView.as_view(), name='tweet_list'),
    path('tweet/new/', TweetCreateView.as_view(), name='tweet_create'),
    path('tweet/<int:pk>/delete/', TweetDeleteView.as_view(), name='tweet_delete'),
    path('tweet/<int:pk>/edit/', TweetUpdateView.as_view(), name='tweet_edit'),
    path('tweet/<int:pk>/', TweetDetailView.as_view(), name='tweet_detail'),
    path('signup/', register, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile_user/<int:user_id>/', views.user_view, name='profile_user'),
    path('tweet/<int:tweet_id>/comment/', CommentCreateView.as_view(), name='commnent_create'),
]
