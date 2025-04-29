# news/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, SourceViewSet, CategoryViewSet
from . import views

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'sources', SourceViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/boolean/', views.boolean_search_view, name='boolean_search'),
]
