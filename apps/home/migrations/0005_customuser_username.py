# Generated by Django 3.2.6 on 2023-10-22 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_customuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default='default_username', max_length=255, verbose_name='Username'),
        ),
    ]
