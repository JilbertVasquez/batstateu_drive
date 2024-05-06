from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class Users(models.Model):
    userid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'users'


class FileDetails(models.Model):
    file_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    extension = models.CharField(max_length=50)
    upload_date = models.DateField()
    key = models.BinaryField(max_length=255)  # Provide a default value
    path = models.TextField()  # Change to TextField to accommodate longer strings

    def set_paths(self, paths_list):
        self.path = '|'.join(paths_list)  # Use '|' as delimiter

    def get_paths(self):
        return self.path.split('|') if self.path else []  # Split by '|' to get list, empty list if path is empty

    class Meta:
        db_table = 'file_details'


class SharingFiles(models.Model):
    share_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE, null=True)  # Allow null values temporarily
    filename = models.CharField(max_length=255)
    extension = models.CharField(max_length=10)
    share_by = models.CharField(max_length=255)
    share_to = models.CharField(max_length=255)
    path = models.CharField(max_length=1000)

    class Meta:
        db_table = 'share_files'