from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('denied/', views.access_denied, name='access_denied'),
    path('projects/', views.show_projects, name='project_list'),
    path('projects/create', views.create_project, name='create_project'),
    path('project/<str:project_pk>/update', views.update_project, name='update_project'),
    path('project/<str:project_pk>/delete', views.delete_project, name='delete_project'),
    path('project/<str:project_pk>/', views.view_project, name='view_project'),
    path('project/<str:project_pk>/tags', views.tag_list, name='tag_list'),
    path('project/<str:project_pk>/tag/create', views.tag_create, name='tag_create')
]
