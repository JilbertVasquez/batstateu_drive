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
    # path('', views.signupPage, name='signup'),
    path('addaccount/', views.addaccount, name='addaccount'),
    path('login/', views.loginPage, name='login'),
    path('', views.loginPage2, name='login2'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('handle_file_upload/', views.handle_file_upload, name='handle_file_upload'),
    path('handle_folder_upload/', views.handle_folder_upload, name='handle_folder_upload'),
    path('download/', views.download_file, name='download_file'),
    path('delete_item/', views.delete_item, name='delete_item'),
    path('view_folder/<path:folder_path>/', views.view_folder, name='view_folder'),
    path('handle_create_folder/', views.handle_create_folder, name='handle_create_folder'),
    path('rename/file/', views.rename_file, name='rename_file'),
    path('rename/folder/', views.rename_folder, name='rename_folder'),
    path('search/', views.search, name='search'),
    path('logout/', views.logout, name='logout'),
    path('share_file/', views.share_file, name='share_file'),
    path('share_files_section', views.share_files_section, name='share_files_section'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),  # URL pattern for disk usage view
    path('disk_usage_view/', views.disk_usage_view, name='disk_usage_view'),
    path('users_admin/', views.users_admin, name='users_admin'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('save_edit_account/', views.save_edit_account, name='save_edit_account'),
    path('new_pass/', views.new_pass, name='new_pass'),
    path('save_new_pass_acc/', views.save_new_pass_acc, name='save_new_pass_acc'),
    path('trackfiledetails/', views.trackfiledetails, name='trackfiledetails'), 
    path('view_file_details/', views.view_file_details, name='view_file_details'), 
    path('tracksharefiles/', views.tracksharefiles, name='tracksharefiles'), 
    path('view_share_files/', views.view_share_files, name='view_share_files'), 
    
]
