# Generated by Django 3.2.6 on 2023-10-22 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_customuser_azienda'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email'),
        ),
    ]