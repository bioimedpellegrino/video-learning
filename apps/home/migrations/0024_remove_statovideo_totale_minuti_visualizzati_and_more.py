# Generated by Django 4.2.6 on 2023-10-30 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_statovideo_data_completamento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statovideo',
            name='totale_minuti_visualizzati',
        ),
        migrations.AddField(
            model_name='statovideo',
            name='durata_video',
            field=models.IntegerField(blank=True, null=True, verbose_name='Durata del video in secondi'),
        ),
        migrations.AddField(
            model_name='statovideo',
            name='totale_secondi_visualizzati',
            field=models.IntegerField(blank=True, null=True, verbose_name='Totale secondi visualizzati'),
        ),
    ]
