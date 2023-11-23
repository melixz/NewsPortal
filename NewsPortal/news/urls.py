from django.urls import path
from .views import (PostList, PostDetailView)
from django.views.decorators.cache import cache_page

urlpatterns = [
   path('news/', PostList.as_view(), name='post_list'),
   path('news/<int:pk>/', cache_page(60 * 5)(PostDetailView.as_view()), name='some_news'),
]