# Generated by Django 4.2.6 on 2023-10-23 16:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0013_alter_azienda_staff_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attestativideo',
            name='utente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Utente'),
        ),
        migrations.AlterField(
            model_name='attestativideo',
            name='video_corso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.videocorso', verbose_name='Video Corso'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='azienda',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='utenti', to='home.azienda', verbose_name='Azienda'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='statovideo',
            name='utente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stati_video', to=settings.AUTH_USER_MODEL, verbose_name='Utente'),
        ),
    ]