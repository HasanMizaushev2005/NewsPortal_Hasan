from django.forms import DateInput
from django_filters import FilterSet, DateFilter, ModelChoiceFilter, CharFilter
from .models import Post, Author


class PostFilter(FilterSet):
    author_name = ModelChoiceFilter(field_name='author',
                                    queryset=Author.objects.all(),
                                    label='Автор',
                                    empty_label='все авторы',
                                    lookup_expr='exact',)

    date = DateFilter(label='Дата публикации',
                      field_name='datetime',
                      lookup_expr='date',
                      widget=DateInput(attrs={'type': 'date'}))

    title = CharFilter(field_name='title',
                       label='Заголовок',
                       lookup_expr='icontains')

    class Meta:
        model = Post
        fields = []