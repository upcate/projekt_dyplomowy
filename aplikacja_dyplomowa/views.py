import os

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
    FilesUpdateForm,
    MainFilesForm,
    MainFileUpdateForm,
)

from .models import Projects, ProjectObjects, Tags, Files, MainFiles

from django.db import IntegrityError, transaction

from django.core.paginator import Paginator

from django.http import FileResponse


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

    if request.method == 'POST':
        form = FilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    file = form.save(commit=False)
                    file.project = project
                    file.user = request.user
                    file.save()
                    return redirect('project_file_view', project_pk=project.id, file_pk=file.id)
            except IntegrityError:
                form.add_error(None, 'Plik o takiej nazwie już istnieje')
                file_path = file.file.path
                os.remove(file_path)

    form_errors = form.errors

    context = {
        'form': form,
        'project': project,
        'form_errors': form_errors,
    }
    return render(request, 'project_structure/files/file_upload.html', context)


@login_required(login_url='login')
def project_file_view(request, project_pk, file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        file = Files.objects.get(id=file_pk)
        if file.user != request.user:
            return redirect('access_denied')
    except Files.DoesNotExist:
        return redirect('project_file_list', project_pk=project.id)

    context = {
        'project': project,
        'file': file,
        'file_size': round(file.file.size / 1024, 2)
    }
    return render(request, 'project_structure/files/file_view.html', context)


@login_required(login_url='login')
def project_file_delete(request, project_pk, file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        file = Files.objects.get(id=file_pk)
        if file.user != request.user:
            return redirect('access_denied')
    except Files.DoesNotExist:
        return redirect('project_file_list', project_pk=project.id)

    if request.method == 'POST':
        file.delete()
        return redirect('project_file_list', project_pk=project.id)

    context = {
        'project': project,
        'file': file,
    }
    return render(request, 'project_structure/files/file_delete.html', context)


@login_required(login_url='login')
def project_file_update(request, project_pk, file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        file = Files.objects.get(id=file_pk)
        if file.user != request.user:
            return redirect('access_denied')
    except Files.DoesNotExist:
        return redirect('project_file_list', project_pk=project.id)

    form = FilesUpdateForm(instance=file)
    if request.method == 'POST':
        form = FilesUpdateForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            try:
                form.save()
                return redirect('project_file_view', project_pk=project.id, file_pk=file.id)
            except IntegrityError:
                form.add_error(None, 'Plik o takiej nazwie już istnieje.')

    context = {
        'file': file,
        'project': project,
        'form': form,
    }
    return render(request, 'project_structure/files/file_update.html', context)


@login_required(login_url='login')
def project_file_download(request, project_pk, file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        file = Files.objects.get(id=file_pk)
        if file.user != request.user:
            return redirect('access_denied')
    except Files.DoesNotExist:
        return redirect('project_file_list', project_pk=project.id)

    return FileResponse(file.file, as_attachment=True)


@login_required(login_url='login')
def main_file_list(request, project_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    main_files = MainFiles.objects.filter(project=project)

    paginator = Paginator(main_files, 5)
    page_number = request.GET.get('page')
    page_main_files = paginator.get_page(page_number)

    context = {
        'project': project,
        'main_files': main_files,
        'page_main_files': page_main_files,
    }
    return render(request, 'project_structure/main_files/main_file_list.html', context)


@login_required(login_url='login')
def main_file_upload(request, project_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    form = MainFilesForm()

    if request.method == 'POST':
        form = MainFilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    main_file = form.save(commit=False)
                    main_file.project = project
                    main_file.user = request.user
                    main_file.save()
                    return redirect('main_file_view', project_pk=project.id, main_file_pk=main_file.id)
            except IntegrityError:
                form.add_error(None, 'Plik o takiej nazwie już istnieje')
                file_path = main_file.file.path
                os.remove(file_path)

    form_errors = form.errors

    context = {
        'form': form,
        'project': project,
        'form_errors': form_errors,
    }
    return render(request, 'project_structure/main_files/main_file_upload.html', context)


@login_required(login_url='login')
def main_file_update(request, project_pk, main_file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        main_file = Files.objects.get(id=main_file_pk)
        if main_file.user != request.user:
            return redirect('access_denied')
    except MainFiles.DoesNotExist:
        return redirect('main_file_list', project_pk=project.id)

    form = MainFileUpdateForm(instance=main_file)
    if request.method == 'POST':
        form = MainFileUpdateForm(request.POST, request.FILES, instance=main_file)
        if form.is_valid():
            try:
                form.save()
                return redirect('main_file_view', project_pk=project.id, main_file_pk=main_file.id)
            except IntegrityError:
                form.add_error(None, 'Plik o takiej nazwie już istnieje.')

    context = {
        'main_file': main_file,
        'project': project,
        'form': form,
    }
    return render(request, 'project_structure/main_files/main_file_update.html', context)


@login_required(login_url='login')
def main_file_delete(request, project_pk, main_file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        main_file = MainFiles.objects.get(id=main_file_pk)
        if main_file.user != request.user:
            return redirect('access_denied')
    except MainFiles.DoesNotExist:
        return redirect('main_file_list', project_pk=project.id)

    if request.method == 'POST':
        main_file.delete()
        return redirect('main_file_list', project_pk=project.id)

    context = {
        'project': project,
        'main_file': main_file,
    }
    return render(request, 'project_structure/main_files/main_file_delete.html', context)


@login_required(login_url='login')
def main_file_view(request, project_pk, main_file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        main_file = MainFiles.objects.get(id=main_file_pk)
        if main_file.user != request.user:
            return redirect('access_denied')
    except MainFiles.DoesNotExist:
        return redirect('main_file_list', project_pk=project.id)

    context = {
        'project': project,
        'main_file': main_file,
        'main_file_size': round(main_file.file.size / 1024, 2)
    }
    return render(request, 'project_structure/main_files/main_file_view.html', context)


@login_required(login_url='login')
def main_file_download(request, project_pk, main_file_pk):
    try:
        project = Projects.objects.get(id=project_pk)
        if project.user != request.user:
            return redirect('access_denied')
    except Projects.DoesNotExist:
        return redirect('project_list')

    try:
        main_file = MainFiles.objects.get(id=main_file_pk)
        if main_file.user != request.user:
            return redirect('access_denied')
    except MainFiles.DoesNotExist:
        return redirect('main_file_list', project_pk=project.id)

    return FileResponse(main_file.file, as_attachment=True)


def handle_not_found(request, exception):
    return render(request, 'main_structure/404.html')


def handle_500(request, exception):
    return render(request, 'main_structure/500.html')
