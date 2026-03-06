from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    View, CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ProjectForm, UserForm, CommentForm
from .models import Project, Category, User, Comment

PROJECTS_PER_PAGE = 5


def prepared_projects(projects=None, *, user=None,
                      only_published=True,
                      annotate_comments=True,
                      annotate_votes=True):
    qs = projects if projects is not None else Project.objects.all()
    qs = qs.select_related('author', 'category')

    annotations = {}
    if annotate_comments:
        annotations['comment_count'] = Count('comments', distinct=True)
    if annotate_votes:
        annotations['vote_count'] = Count('votes', distinct=True)
    if user and user.is_authenticated:
        liked = Project.votes.through.objects.filter(
            project_id=OuterRef('pk'),
            user_id=user.pk
        )
        annotations['is_voted'] = Exists(liked)
    if annotations:
        qs = qs.annotate(**annotations)
    if only_published:
        public_filter = Q(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
        if user and user.is_authenticated:
            qs = qs.filter(public_filter | Q(author=user))
        else:
            qs = qs.filter(public_filter)

    return qs.order_by('-pub_date').distinct()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин проверки авторства с умным редиректом."""
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        project_id = self.kwargs.get('project_id')
        return redirect('project:project_detail', project_id=project_id)


class ProjectBaseMixin(LoginRequiredMixin, OnlyAuthorMixin):
    model = Project
    template_name = 'project/create.html'
    pk_url_kwarg = 'project_id'


class CategoryFormMixin:

    def form_valid(self, form):
        title = form.cleaned_data['category_name']
        form.instance.category = Category.get_or_create_by_title(title)
        return super().form_valid(form)


class CommentBaseMixin(LoginRequiredMixin, OnlyAuthorMixin):
    model = Comment
    template_name = 'project/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('project:project_detail',
                       args=[self.kwargs['project_id']])


class ProjectListView(ListView):
    model = Project
    template_name = 'project/index.html'
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        return prepared_projects(user=self.request.user)


class ProjectDetailView(DetailView):
    model = Project
    pk_url_kwarg = 'project_id'
    template_name = 'project/detail.html'

    def get_queryset(self):
        return prepared_projects(user=self.request.user,
                                 annotate_comments=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class ProjectCreateView(LoginRequiredMixin, CategoryFormMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project:project_detail', args=[self.object.pk])


class ProjectUpdateView(ProjectBaseMixin, CategoryFormMixin, UpdateView):
    form_class = ProjectForm

    def get_success_url(self):
        return reverse('project:project_detail', args=[self.object.pk])


class ProjectDeleteView(ProjectBaseMixin, DeleteView):
    def get_success_url(self):
        return reverse('project:profile', args=[self.request.user.username])


class CategoryListView(ListView):
    template_name = 'project/category.html'
    paginate_by = PROJECTS_PER_PAGE

    def get_category(self):
        if not hasattr(self, '_category'):
            self._category = get_object_or_404(
                Category, slug=self.kwargs['category_slug'], is_published=True
            )
        return self._category

    def get_queryset(self):
        return prepared_projects(
            projects=self.get_category().projects.all(),
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(category=self.get_category(), **kwargs)


class ProfileView(ListView):
    template_name = 'project/profile.html'
    paginate_by = PROJECTS_PER_PAGE

    def get_author(self):
        if not hasattr(self, '_author'):
            self._author = get_object_or_404(User,
                                             username=self.kwargs['username'])
        return self._author

    def get_queryset(self):
        return prepared_projects(
            projects=self.get_author().projects.all(),
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(profile=self.get_author(), **kwargs)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'project/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('project:profile', args=[self.request.user.username])


class VoteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.votes.filter(id=request.user.id).exists():
            project.votes.remove(request.user)
        else:
            project.votes.add(request.user)
        return redirect(request.META.get('HTTP_REFERER', 'project:index'))


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.project = get_object_or_404(Project,
                                                  pk=self.kwargs['project_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project:project_detail',
                       args=[self.kwargs['project_id']])


class CommentUpdateView(CommentBaseMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentBaseMixin, DeleteView):
    pass
