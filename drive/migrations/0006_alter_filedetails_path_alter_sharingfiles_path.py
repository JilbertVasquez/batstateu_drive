# Generated by Django 5.0.3 on 2024-04-19 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0005_rename_user_id_filedetails_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filedetails',
            name='path',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='sharingfiles',
            name='path',
            field=models.CharField(max_length=1000),
        ),
    ]
