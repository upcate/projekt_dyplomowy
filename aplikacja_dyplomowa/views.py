from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    CreateUserForm,
    ProjectForm,
    TagForm,
    ProjectObjectForm,
    ProjectObjectAddTagForm,
    ProjectObjectAddConnectionForm,
    UpdateUserForm,
    CustomPasswordChangeForm,
    FilesForm,
)

from .models import Projects, ProjectObjects, Tags, Files

from django.db import IntegrityError

from django.core.paginator import Paginator

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
def account_view(request):

    user = request.user

    context = {
        'user': user
    }
    return render(request, 'accounts/account_view.html', context)


@login_required(login_url='login')
def account_update(request):

    user = request.user
    form = UpdateUserForm(instance=user, user=user)
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user, user=user)
        if form.is_valid():
            form.save()
            return redirect('account_view')

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'accounts/account_update.html', context)


@login_required(login_url='login')
def account_update_password(request):

    user = request.user
    form = CustomPasswordChangeForm(user)

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostało zmienione pomyślnie.')
            return redirect('account_update_password')

    context = {
        'form': form,
    }
    return render(request, 'accounts/account_update_password.html', context)


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
                return redirect('view_project', project_pk=project.id)
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

    form = TagForm(instance=tag)
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


@login_required(login_url='login')
def object_list(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    context = {
        'project': project,
        'objects': ProjectObjects.objects.filter(project=project)
    }
    return render(request, 'project_structure/object/object_list.html', context)


@login_required(login_url='login')
def object_create(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    form = ProjectObjectForm()
    if request.method == 'POST':
        form = ProjectObjectForm(request.POST)
        user = request.user
        if form.is_valid():
            try:
                object_to_save = form.save(commit=False)
                object_to_save.user = user
                object_to_save.project = project
                object_to_save.save()
                return redirect('object_view', project_pk=project.id, object_pk=object_to_save.id)
            except IntegrityError:
                form.add_error(None, 'Obiekt o takiej nazwie już istnieje.')

    context = {
        'form': form,
        'project': project
    }
    return render(request, 'project_structure/object/object_create.html', context)


@login_required(login_url='login')
def object_update(request, project_pk, object_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        object_to_update = ProjectObjects.objects.get(id=object_pk)
        if object_to_update.user != request.user:
            return redirect('access_denied')
    except ProjectObjects.DoesNotExist:
        return redirect('object_list', project_pk=project.id)

    form = ProjectObjectForm(instance=object_to_update)
    if request.method == 'POST':
        form = ProjectObjectForm(request.POST, instance=object_to_update)
        if form.is_valid():
            try:
                form.save()
                return redirect('object_view', project_pk=project.id, object_pk=object_to_update.id)
            except IntegrityError:
                form.add_error(None, 'Obiekt o takiej nazwie już istnieje.')

    context = {
        'form': form,
        'project': project,
        'object': object_to_update,
    }
    return render(request, 'project_structure/object/object.update.html', context)


@login_required(login_url='login')
def object_delete(request, project_pk, object_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        object_to_delete = ProjectObjects.objects.get(id=object_pk)
        if object_to_delete.user != request.user:
            return redirect('access_denied')
    except ProjectObjects.DoesNotExist:
        return redirect('object_list', project_pk=project.id)

    form = ProjectObjectForm()
    if request.method == 'POST':
        object_to_delete.delete()
        return redirect('object_list', project_pk=project.id)

    context = {
        'form': form,
        'object': object_to_delete,
        'project': project
    }
    return render(request, 'project_structure/object/object_delete.html', context)


@login_required(login_url='login')
def object_view(request, project_pk, object_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        object_to_view = ProjectObjects.objects.get(id=object_pk)
        if object_to_view.user != request.user:
            return redirect('access_denied')
    except ProjectObjects.DoesNotExist:
        return redirect('object_list', project_pk=project.id)

    tags = object_to_view.tags.all()
    connections = object_to_view.connections.all()

    context = {
        'object': object_to_view,
        'project': project,
        'tags': tags,
        'connections': connections
    }
    return render(request, 'project_structure/object/object_view.html', context)


@login_required(login_url='login')
def object_tag_edit(request, project_pk, object_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        object_to_view = ProjectObjects.objects.get(id=object_pk)
        if object_to_view.user != request.user:
            return redirect('access_denied')
    except ProjectObjects.DoesNotExist:
        return redirect('object_list', project_pk=project.id)

    form = ProjectObjectAddTagForm(project=project, object_to_view=object_to_view)
    tags = Tags.objects.filter(project=project)

    if request.method == 'POST':
        form = ProjectObjectAddTagForm(request.POST, project=project, object_to_view=object_to_view)
        if form.is_valid():
            tags_from_form = form.cleaned_data['tags']
            current_tags = set(object_to_view.tags.all())

            tags_to_add = set(tags_from_form) - current_tags
            tags_to_remove = current_tags - set(tags_from_form)

            for tag in tags_to_add:
                object_to_view.tags.add(tag)

            for tag in tags_to_remove:
                object_to_view.tags.remove(tag)

            return redirect('object_view', project_pk=project.id, object_pk=object_to_view.id)

    context = {
        'form': form,
        'project': project,
        'object': object_to_view,
        'tags': tags,
    }
    return render(request, 'project_structure/object/object_tag_edit.html', context)


@login_required(login_url='login')
def object_connections_edit(request, project_pk, object_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        object_to_view = ProjectObjects.objects.get(id=object_pk)
        if object_to_view.user != request.user:
            return redirect('access_denied')
    except ProjectObjects.DoesNotExist:
        return redirect('object_list', project_pk=project.id)

    form = ProjectObjectAddConnectionForm(project=project, object_to_view=object_to_view)
    objects = ProjectObjects.objects.filter(project=project)

    if request.method == 'POST':
        form = ProjectObjectAddConnectionForm(request.POST, project=project, object_to_view=object_to_view)
        if form.is_valid():
            connections_from_form = form.cleaned_data['connections']
            current_connections = set(object_to_view.connections.all())

            connections_to_add = set(connections_from_form) - current_connections
            connections_to_remove = current_connections - set(connections_from_form)

            for connection in connections_to_add:
                object_to_view.connections.add(connection)

            for connection in connections_to_remove:
                object_to_view.connections.remove(connection)

            return redirect('object_view', project_pk=project.id, object_pk=object_to_view.id)

    context = {
        'form': form,
        'object': object_to_view,
        'project': project,
        'objects': objects,
    }
    return render(request, 'project_structure/object/object_connections_edit.html', context)


@login_required(login_url='login')
def objects_by_tag(request, project_pk, tag_pk):

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
        return redirect('view_project', project_pk=project.id)

    objects = ProjectObjects.objects.filter(tags__id=tag.id)

    paginator = Paginator(objects, 5)
    page_number = request.GET.get('page')
    page_objects = paginator.get_page(page_number)

    context = {
        'project': project,
        'tag': tag,
        'objects': objects,
        'page_objects': page_objects
    }
    return render(request, 'project_structure/object/objects_by_tag.html', context)


@login_required(login_url='login')
def project_file_list(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    files = Files.objects.filter(project=project)

    paginator = Paginator(files, 5)
    page_number = request.GET.get('page')
    page_files = paginator.get_page(page_number)

    context = {
        'project': project,
        'files': files,
        'page_files': page_files,
    }
    return render(request, 'project_structure/files/file_list.html', context)


@login_required(login_url='login')
def project_file_upload(request, project_pk):

    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    form = FilesForm()

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'project_structure/files/file_upload.html', context)
