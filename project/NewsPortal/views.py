from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.contrib.auth.mixins import PermissionRequiredMixin

from .forms import PostForm
from .models import Post
from .filters import PostFilter
from .utils import create_or_update


class PostListView(ListView):
    model = Post
    ordering = '-datetime'
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


class PostSearchView(FilterView):
    model = Post
    ordering = '-datetime'
    template_name = 'post_search.html'
    context_object_name = 'posts'
    paginate_by = 10
    filterset_class = PostFilter


class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_create_or_update.html'
    permission_required = 'NewsPortal.add_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return create_or_update(context, self.request.path)

    def form_valid(self, form):
        post = form.save(commit=False)

        if 'articles' in self.request.path:
            post.positions = 'СТ'

        post.save()
        return super().form_valid(form)


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_create_or_update.html'
    permission_required = 'NewsPortal.change_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return create_or_update(context, self.request.path)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post
    context_object_name = 'post'
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'NewsPortal.delete_post'