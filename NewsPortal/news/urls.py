from django.contrib import admin
from django.urls import include
from django.urls import path
from .views import (PostList, PostDetailView, PostCreate, PostUpdate, PostDelete, SearchResultsView, ArticleDelete,
                    ArticleUpdate, ArticleCreate, ArticleDetailView)
from django.views.decorators.cache import cache_page

urlpatterns = [
   path('', PostList.as_view(), name='post_list'),
   path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
   path('search/', SearchResultsView.as_view(), name='search'),
   path('news/<int:pk>/', cache_page(60 * 5)(PostDetailView.as_view()), name='some_news'),
   path('news/create/', PostCreate.as_view(), name='new_post'),
   path('news/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
   path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('search/', SearchResultsView.as_view(), name='search'),
   path('article/<int:pk>/', cache_page(60 * 5)(ArticleDetailView.as_view()), name='article'),
   path('article/create/', ArticleCreate.as_view(), name='new_article'),
   path('article/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_edit'),
   path('article/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
   path('admin/', admin.site.urls),
   path('', include('protect.urls')),
   path('sign/', include('sign.urls')),
   path('accounts/', include('allauth.urls')),
]
