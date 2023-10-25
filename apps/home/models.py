from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User  

class Azienda(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    nome = models.CharField(max_length=255, verbose_name="Nome Azienda")
    staff_users = models.ManyToManyField('CustomUser', related_name='aziende', blank=True)

    def __str__(self):
        return self.nome
    
    def get_utenti_serialized(self):
        return [{
            "id": utente.pk, 
            "first_name": utente.user.first_name if utente.user.first_name else "",
            "last_name": utente.user.last_name if utente.user.last_name else "",
            "email": utente.user.email if utente.user.email else "",
            "phone": utente.phone_number if utente.phone_number else ""
            } 
        for utente in self.utenti.all()]
    
    def to_json(self):
        return {
            "nome": self.nome,
            "utenti": [utente.pk for utente in self.utenti.all()]
        }
    
    class Meta:
        verbose_name = "Azienda"
        verbose_name_plural = "Aziende"

class CustomUser(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    azienda = models.ForeignKey(Azienda, on_delete=models.SET_NULL, related_name="utenti", verbose_name="Azienda", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
    @property
    def is_only_student(self):
        return not any([self.user.is_superuser, self.user.is_staff])

    class Meta:
        verbose_name = "Profilo"
        verbose_name_plural = "Profili"

class VideoCorso(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    titolo = models.CharField(max_length=255, verbose_name="Titolo Video")
    descrizione = models.TextField(blank=True, null=True)
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
    utente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="stati_video", verbose_name="Utente")
    video_corso = models.ForeignKey(VideoCorso, on_delete=models.CASCADE, related_name="stati_video", verbose_name="Video Corso")
    visualizzato = models.BooleanField(default=False, verbose_name="Visualizzato")
    completato = models.BooleanField(default=False, verbose_name="Completato")
    data_prima_visual = models.DateTimeField(blank=True, null=True, verbose_name="Data prima apertura del video")
    data_ultima_visual = models.DateTimeField(blank=True, null=True, verbose_name="Data ultima apertura del video")
    totale_minuti_visualizzati = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.utente.username} - {self.video_corso.titolo} - {'Visualizzato' if self.visualizzato else 'Non Visualizzato'}"    
    class Meta:
        unique_together = (("utente", "video_corso"),)
        verbose_name_plural = "Stati Video"
        verbose_name = "Stato Video"

class AttestatiVideo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    utente = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name="Utente")
    video_corso = models.ForeignKey(VideoCorso, null=True, on_delete=models.SET_NULL, verbose_name="Video Corso")
    data_conseguimento = models.DateTimeField(blank=True, null=True, verbose_name="Data conseguimento")
    data_download = models.DateTimeField(blank=True, null=True, verbose_name="Data download")
    pdf = models.FileField(blank=True, null=True, upload_to="attestati/")
    
    def __str__(self):
        return f"{self.utente.username} - {self.video_corso.titolo}"