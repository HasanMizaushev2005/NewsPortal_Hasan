from django.forms import ModelForm
from .models import Post


class PostForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['author'].empty_label = 'Выберите автора'

    class Meta:
        model = Post
        fields = ['author', 'title', 'text', 'category']
        labels = {
            'author': 'Автор',
            'title': 'Заголовок',
            'text': 'Содержание',
            'category': 'Категория',
        }
