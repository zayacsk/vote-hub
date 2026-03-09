from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, CategoryViewSet, CommentViewSet


router_v1 = DefaultRouter()
router_v1.register(r'projects', ProjectViewSet, basename='projects')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(
    r'projects/(?P<project_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls.jwt')),
]
