from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from django.contrib import messages
from .models import Projects, ProjectObjects, Tags, Files

# Create your views here.


def main(request):

    return render(request, 'main_structure/main.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:

        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, f'Użytkownik {user} zarejestrowany pomyślnie!')
                return redirect('login')

        context = {
            'form': form
        }
        return render(request, 'accounts/register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('main')
            else:
                messages.info(request, 'Hasło lub użytkownik są niepoprawne')

        return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('main')


@login_required(login_url='login')
def show_projects(request):
    context = {
        'projects': Projects.objects.filter(user=request.user)
    }

    return render(request, 'project_strucutre/project_list.html', context)
