from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
'''
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        
        username = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff="True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser="True.')
        
        return self.create_user(username, password, **extra_fields)
    
    
class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True, default='default_username')
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['firstname', 'lastname']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username
    
    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label` in the admin interface?
        """
        return True  # Or implement your custom logic here
        
'''

from django.db import models

class Users(models.Model):
    userid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'Users'  # Specify the name of the table in the database
