from django.contrib import admin

from django.contrib import admin

from .models import Users, FileDetails, SharingFiles

admin.site.register(Users)
admin.site.register(FileDetails)
admin.site.register(SharingFiles)