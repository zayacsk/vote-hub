from django.urls import path

from . import views

app_name = 'project'


urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('projects/create/',
         views.ProjectCreateView.as_view(),
         name='create_project'),
    path('projects/<int:project_id>/edit/',
         views.ProjectUpdateView.as_view(),
         name='edit_project'),
    path('projects/<int:project_id>/delete/',
         views.ProjectDeleteView.as_view(),
         name='delete_project'),
    path('projects/<int:project_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('projects/<int:project_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('projects/<int:project_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('profile/my/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/',
         views.ProfileView.as_view(),
         name='profile'),
    path('projects/<int:project_id>/',
         views.ProjectDetailView.as_view(),
         name='project_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_projects'),
    path('projects/<int:project_id>/vote/',
         views.VoteView.as_view(),
         name='vote'),
]
