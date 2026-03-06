from django.contrib import admin

from .models import Category, Project, Comment

admin.site.register(Category)
admin.site.register(Project)
admin.site.register(Comment)
