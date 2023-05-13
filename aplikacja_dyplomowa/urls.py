from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.account_view, name='account_view'),
    path('profile/update', views.account_update, name='account_update'),
    path('profile/password/update', views.account_update_password, name='account_update_password'),
    path('denied/', views.access_denied, name='access_denied'),
    path('projects/', views.show_projects, name='project_list'),
    path('projects/create', views.create_project, name='create_project'),
    path('project/<str:project_pk>/update', views.update_project, name='update_project'),
    path('project/<str:project_pk>/delete', views.delete_project, name='delete_project'),
    path('project/<str:project_pk>/', views.view_project, name='view_project'),
    path('project/<str:project_pk>/tags', views.tag_list, name='tag_list'),
    path('project/<str:project_pk>/tag/create', views.tag_create, name='tag_create'),
    path('project/<str:project_pk>/tag/<str:tag_pk>/update', views.tag_update, name='tag_update'),
    path('project/<str:project_pk>/tag/<str:tag_pk>/delete', views.tag_delete, name='tag_delete'),
    path('project/<str:project_pk>/objects', views.object_list, name='object_list'),
    path('project/<str:project_pk>/object/create', views.object_create, name='object_create'),
    path('project/<str:project_pk>/object/<str:object_pk>/update', views.object_update, name='object_update'),
    path('project/<str:project_pk>/object/<str:object_pk>/delete', views.object_delete, name='object_delete'),
    path('project/<str:project_pk>/object/<str:object_pk>', views.object_view, name='object_view'),
    path('project/<str:project_pk>/object/<str:object_pk>/tags/edit', views.object_tag_edit, name='object_tags_edit'),
    path('project/<str:project_pk>/object/<str:object_pk>/connections/edit', views.object_connections_edit, name='objects_connections_edit'),


]
