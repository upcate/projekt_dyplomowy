from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, ProjectForm, TagForm
from django.contrib import messages
from .models import Projects, ProjectObjects, Tags, Files
from django.db import IntegrityError

# Create your views here.


def main(request):

    return render(request, 'main_structure/main.html')


@login_required(login_url='login')
def access_denied(request):
    return render(request, 'main_structure/access_denied.html')


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
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect('main')
            else:
                messages.info(request, 'Hasło lub użytkownik są niepoprawne')

        return render(request, 'accounts/login.html')


def logout_user(request):

    logout(request)
    return redirect('main')


@login_required(login_url='login')
def show_projects(request):

    projects = Projects.objects.filter(user=request.user)

    context = {
        'projects': projects
    }
    return render(request, 'project_structure/project_list.html', context)


@login_required(login_url='login')
def create_project(request):

    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        user = request.user
        if form.is_valid():
            try:
                project = form.save(commit=False)
                project.user = user
                project.save()
                # Na razie redirectuje do listy projektów, ale jak dodam widok obiektu, to po stworzeniu tam go
                # przedirectuje
                return redirect('view_project', project_pk=project.id)
            except IntegrityError:
                form.add_error(None, 'Projekt o tej nazwie już istnieje.')

    context = {
        'form': form,
    }
    return render(request, 'project_structure/project_create.html', context)


@login_required(login_url='login')
def update_project(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            try:
                form.save()
                # Na razie redirectuje do listy, fajnie by było, gdyby w zależności od tego, czy edytowałeś z listy
                # projektów, czy z widoku projektu, żeby tam cię przerzucał
                return redirect('project_list')
            except IntegrityError:
                form.add_error(None, 'Projekt o tej nazwie już istnieje.')

    context = {
        'form': form,
        'project': project
    }
    return render(request, 'project_structure/project_update.html', context)


@login_required(login_url='login')
def delete_project(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    form = ProjectForm(instance=project)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')

    context = {
        'form': form,
        'project': project
    }
    return render(request, 'project_structure/project_delete.html', context)


@login_required(login_url='login')
def view_project(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    context = {
        'project': project,
        'objects': ProjectObjects.objects.filter(project=project),
        'tags': Tags.objects.filter(project=project),
        'files': Files.objects.filter(project=project)
    }
    return render(request, 'project_structure/project_view.html', context)


@login_required(login_url='login')
def tag_list(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    context = {
        'project': project,
        'tags': Tags.objects.filter(project=project)
    }
    return render(request, 'project_structure/tags/tag_list.html', context)


@login_required(login_url='login')
def tag_create(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    form = TagForm()
    if request.method == 'POST':
        form = TagForm(request.POST)
        user = request.user

        if form.is_valid():
            try:
                tag = form.save(commit=False)
                tag.project = project
                tag.user = user
                tag.save()
                return redirect('tag_list', project_pk=project.id)
            except IntegrityError:
                form.add_error(None, 'Tag o takiej nazwie już istnieje.')

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'project_structure/tags/tag_create.html', context)


@login_required(login_url='login')
def tag_update(request, project_pk, tag_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        tag = Tags.objects.get(id=tag_pk, project=project)
        if tag.user != request.user:
            return redirect('access_denied')
    except Tags.DoesNotExist:
        return redirect('tag_list', project_pk=project_pk)

    form = TagForm()
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            try:
                form.save()
                return redirect('tag_list', project_pk=project.id)
            except IntegrityError:
                form.add_error(None, 'Tag o takiej nazwie już istnieje')

    context = {
        'project': project,
        'tag': tag,
        'form': form,
    }
    return render(request, 'project_structure/tags/tag_update.html', context)


@login_required(login_url='login')
def tag_delete(request, project_pk, tag_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        tag = Tags.objects.get(id=tag_pk)
        if tag.user != request.user:
            return redirect('access_denied')
    except Tags.DoesNotExist:
        return redirect('tag_list', project_pk=project.id)

    form = TagForm(instance=tag)
    if request.method == 'POST':
        tag.delete()
        return redirect('tag_list', project_pk=project.id)

    context = {
        'project': project,
        'tag': tag,
        'form': form,
    }
    return render(request, 'project_structure/tags/tag_delete.html', context)
