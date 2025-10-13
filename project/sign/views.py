from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm
from .utils import request_object
from NewsPortal.models import Author


class SignUpView(CreateView):
    model = User
    template_name = 'sign/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('user_profile')


def confirm_logout(request):
    return render(request, 'sign/confirm_logout.html')


@login_required
def user_profile(request):
    context = {
        'is_author': request.user.groups.filter(name='authors').exists(),
    }
    return render(request, 'sign/profile.html', context)


@login_required
def be_author(request):
    request_object(Author, user=request.user)
    group_authors = request_object(Group, name='authors')

    if not request.user.groups.filter(name='authors').exists():
        request.user.groups.add(group_authors)

    list(messages.get_messages(request))
    messages.success(
        request,
        "Вы успешно стали автором!",
        extra_tags='authors'
    )

    return redirect(request.META.get('HTTP_REFERER'))