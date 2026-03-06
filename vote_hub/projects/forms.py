from django import forms
from .models import Project, User, Comment


class ProjectForm(forms.ModelForm):
    category_name = forms.CharField(
        label='Категория',
        required=True,
        help_text='Введите существующую или новую категорию'
    )

    class Meta:
        model = Project
        fields = ('title', 'text', 'category_name', 'is_published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.category:
            self.initial['category_name'] = self.instance.category.title

    def clean_category_name(self):
        data = self.cleaned_data.get('category_name')
        return data.strip()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'cols': 40,
                'placeholder': 'Напишите комментарий...',
                'class': 'form-control'
            }),
        }
