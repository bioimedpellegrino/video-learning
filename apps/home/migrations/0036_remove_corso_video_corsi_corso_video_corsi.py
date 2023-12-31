# Generated by Django 4.2.7 on 2023-12-31 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0035_alter_videocorso_options_videocorso_ordine"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="corso",
            name="video_corsi",
        ),
        migrations.AddField(
            model_name="corso",
            name="video_corsi",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="corsi",
                to="home.videocorso",
                verbose_name="Video Corso",
            ),
        ),
    ]