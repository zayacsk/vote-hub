from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from projects.models import Category, Project, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'slug', 'is_published')


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author')
        read_only_fields = ('author',)

    def create(self, validated_data):
        project_id = self.context['view'].kwargs.get('project_id')
        return Comment.objects.create(project_id=project_id, **validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    category = SlugRelatedField(slug_field='title', read_only=True)
    total_votes = serializers.IntegerField(source='votes_count',
                                           read_only=True)
    total_comments = serializers.IntegerField(source='comments_count',
                                              read_only=True)

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'text',
            'pub_date',
            'author',
            'category',
            'is_published',
            'total_votes',
            'total_comments'
        )
        read_only_fields = ('author', 'pub_date')


class ProjectCreateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True)

    class Meta:
        model = Project
        fields = ('title', 'text', 'category_name', 'is_published')

    def create(self, validated_data):
        category_name = validated_data.pop('category_name')
        category = Category.get_or_create_by_title(category_name)
        project = Project.objects.create(
            category=category,
            author=self.context['request'].user,
            **validated_data
        )
        return project

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category_name', None)
        if category_name:
            instance.category = Category.get_or_create_by_title(category_name)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
