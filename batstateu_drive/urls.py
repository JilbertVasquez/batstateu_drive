"""
URL configuration for batstateu_drive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drive import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signupPage, name='signup'),
    path('login/', views.loginPage, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('handle_file_upload/', views.handle_file_upload, name='handle_file_upload'),
    path('handle_folder_upload/', views.handle_folder_upload, name='handle_folder_upload'),
    path('download/<str:file_name>/', views.download_file, name='download_file'),
    # path('download/<str:file_name>/<str:current_directory>/', views.download_file, name='download_file'),
    path('delete_item/', views.delete_item, name='delete_item'),
    # path('view_folder/<str:folder_name>/', views.view_folder, name='view_folder'),
    path('view_folder/<path:folder_path>/', views.view_folder, name='view_folder'),
    path('handle_create_folder/', views.handle_create_folder, name='handle_create_folder'),
    
]
