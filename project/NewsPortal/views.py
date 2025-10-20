from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from .forms import PostForm
from .models import Post, Category
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
        before_datetime = timezone.now() - timedelta(days=1)
        posts_count = Post.objects.filter(author=self.request.user.author, datetime__gte=before_datetime).count()
        context['posts_limit'] = posts_count < 3
        return create_or_update(context, self.request.path)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
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
    success_url = reverse_lazy('post_list')
    permission_required = 'NewsPortal.delete_post'


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


@login_required
def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER'))