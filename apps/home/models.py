from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User  

class Azienda(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    nome = models.CharField(max_length=255, verbose_name="Nome Azienda")  

    def __str__(self):
        return self.nome

class CustomUser(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    username = models.CharField(max_length=255, verbose_name="Username", default='')
    password = models.CharField(max_length=255, verbose_name="Password", default='Changeme12!')
    nome = models.CharField(max_length=255, verbose_name="Nome")
    cognome = models.CharField(max_length=255, verbose_name="Cognome")
    azienda = models.ForeignKey(Azienda, on_delete=models.CASCADE, related_name="utenti", verbose_name="Azienda", null=True, blank=True)
    email = models.EmailField(max_length=255, verbose_name="Email", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nome + " " + self.cognome

class VideoCorso(models.Model):
    titolo = models.CharField(max_length=255, verbose_name="Titolo Video")
    aziende = models.ManyToManyField(Azienda, related_name="video_corsi", verbose_name="Aziende")
    video_file = models.FileField(
        upload_to='videos/', 
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])],
        verbose_name="File Video",
        blank=True,
    )

    def __str__(self):
        return self.titolo
    
    class Meta:
        verbose_name_plural = "Video Corsi"
        verbose_name = "Video Corso"

class StatoVideo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stati_video", verbose_name="Utente")
    video_corso = models.ForeignKey(VideoCorso, on_delete=models.CASCADE, related_name="stati_video", verbose_name="Video Corso")
    visualizzato = models.BooleanField(default=False, verbose_name="Visualizzato")

    def __str__(self):
        return f"{self.utente.username} - {self.video_corso.titolo} - {'Visualizzato' if self.visualizzato else 'Non Visualizzato'}"    
    class Meta:
        unique_together = (("utente", "video_corso"),)
        verbose_name_plural = "Stati Video"
        verbose_name = "Stato Video"

