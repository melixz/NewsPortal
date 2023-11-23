from django.urls import path
from .views import (PostList, PostDetailView)
from django.views.decorators.cache import cache_page

urlpatterns = [
   path('', PostList.as_view(), name='post_list'),
   path('<int:pk>/', PostDetailView.as_view(), name='post_detail')
]
