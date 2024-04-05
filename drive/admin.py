from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import CustomUser
# Register your models here.

# class CustomUserAdmin(BaseUserAdmin):
#     filter_horizontal = []  # Add your custom fields here
#     ordering = []  # Add your custom ordering here
#     list_display = []  # Add your custom display fields here
#     list_filter = []  # Add your custom filter fields here

# admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import admin
from .models import Users
from .models import FileDetails

admin.site.register(Users)
admin.site.register(FileDetails)