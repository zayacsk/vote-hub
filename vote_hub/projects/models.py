from django.contrib.auth import get_user_model
from django.db import models

from slugify import slugify

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return self.title

    @classmethod
    def get_or_create_by_title(cls, title):
        title = title.strip()
        category, _ = cls.objects.get_or_create(title=title)
        return category

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Project(PublishedModel):
    title = models.CharField('Название', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='projects'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects'
    )
    votes = models.ManyToManyField(User, related_name='vote', blank=True)

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'Проекты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:15]

    def total_votes(self):
        return self.votes.count()


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    project = models.ForeignKey(
        Project,
        verbose_name='Проект',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
