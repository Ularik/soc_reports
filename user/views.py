from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render, reverse
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm
from django.urls import reverse_lazy

User = get_user_model()


def user_login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            print('пользователь существует')
            if user:
                login(request, user)
                print('залогинились')
                print(user.is_active)
                return redirect('reports:report_new')

    form = UserLoginForm()

    return render(request, 'user/login.html', context={'form': form})


@login_required(login_url='/user/login/')
def user_logout_view(request):
    logout(request)
    return redirect('reports:report_new')
