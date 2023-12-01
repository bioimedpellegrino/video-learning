# Generated by Django 4.2.6 on 2023-11-30 23:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0029_domanda_quiz_opzionerisposta_domanda_quiz"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attestativideo",
            options={
                "verbose_name": "Attestato Video",
                "verbose_name_plural": "Attestati Video",
            },
        ),
        migrations.AlterModelOptions(
            name="domanda",
            options={"verbose_name": "Domanda", "verbose_name_plural": "Domande"},
        ),
        migrations.AlterModelOptions(
            name="opzionerisposta",
            options={
                "verbose_name": "OpzioneRisposta",
                "verbose_name_plural": "Opzioni Risposta",
            },
        ),
        migrations.AlterModelOptions(
            name="quiz",
            options={"verbose_name": "Quiz", "verbose_name_plural": "Quiz"},
        ),
        migrations.CreateModel(
            name="QuizAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "quiz",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.quiz"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]