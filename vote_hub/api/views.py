from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from projects.models import Project, Category, Comment
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    CategorySerializer,
    CommentSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_published=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_fields = ('category__title', 'author__username')
    search_fields = ('title', 'text', 'author__username')
    ordering_fields = ('pub_date', 'title', 'votes_count', 'comments_count')

    def get_queryset(self):
        user = self.request.user
        base_qs = Project.objects.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).select_related('author', 'category')
        if user.is_authenticated:
            return base_qs.filter(Q(is_published=True) | Q(author=user))
        else:
            return base_qs.filter(is_published=True)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_object(self):
        obj = super().get_object()
        if not obj.is_published and obj.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This project is not published yet.")
        return obj

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        project = self.get_object()
        project.votes.add(request.user)
        return Response({'votes': project.total_votes()})

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def unvote(self, request, pk=None):
        project = self.get_object()
        project.votes.remove(request.user)
        return Response({'votes': project.total_votes()})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Comment.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
