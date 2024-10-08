from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User  
from django.db.models import JSONField
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    video_corsi_spec = models.ManyToManyField('VideoCorso', related_name="utenti", verbose_name="Video Corsi") # Se l'utente deve avere dei corsi specifici e non tutti quelli associati all'azienda
    
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
    @property
    def is_only_student(self):
        return not any([self.user.is_superuser, self.user.is_staff])

    class Meta:
        verbose_name = "Profilo"
        verbose_name_plural = "Profili"

class Corso(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    titolo = models.CharField(max_length=255, verbose_name="Titolo Corso")
    descrizione = models.TextField(blank=True, null=True)
    aziende = models.ManyToManyField(Azienda, related_name="corsi", verbose_name="Aziende")
    # video_corsi = models.ManyToManyField(VideoCorso, related_name="corsi", verbose_name="Video Corsi")
    docenti = models.ManyToManyField('CustomUser', related_name="corsi_insegnati", verbose_name="Docenti")
    data_inizio = models.DateField(blank=True, null=True, verbose_name="Data inizio")
    data_fine = models.DateField(blank=True, null=True, verbose_name="Data fine")
    durata = models.IntegerField(blank=True, null=True, verbose_name="Durata in giorni")
    data_creazione = models.DateTimeField(auto_now_add=True, verbose_name="Data creazione")

    def __str__(self):
        return self.titolo
    
    class Meta:
        verbose_name_plural = "Corsi"
        verbose_name = "Corso"
class VideoCorso(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    titolo = models.CharField(max_length=255, verbose_name="Titolo Video")
    descrizione = models.TextField(blank=True, null=True)
    aziende = models.ManyToManyField(Azienda, related_name="video_corsi", verbose_name="Aziende")
    ordine = models.PositiveIntegerField(default=0)
    corso = models.ForeignKey(Corso, on_delete=models.CASCADE, related_name="video_corsi", null=True, blank=True, verbose_name="Corso")

    video_file = models.FileField(
        upload_to='videos/', 
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])],
        verbose_name="File Video",
        blank=True,
    )
    poster_file = models.ImageField(
        upload_to='posters/', 
        verbose_name="Miniature foto",
        blank=True,
    )
    external_url = models.CharField(max_length=2000, blank=True, null=True, verbose_name="Url CDN")
    durata_video = models.IntegerField(blank=True, null=True, verbose_name="Durata del video in secondi")

    def __str__(self):
        return self.titolo
    
    class Meta:
        verbose_name_plural = "Video Corsi"
        verbose_name = "Video Corso"
        ordering = ['ordine']

class StatoVideo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    utente = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="stati_video", verbose_name="Utente")
    video_corso = models.ForeignKey(VideoCorso, on_delete=models.SET_NULL, null=True, related_name="stati_video", verbose_name="Video Corso")
    iniziato = models.BooleanField(default=False, verbose_name="Video iniziato")
    completato = models.BooleanField(default=False, verbose_name="Video completato")
    data_prima_visual = models.DateTimeField(blank=True, null=True, verbose_name="Data prima apertura del video")
    data_ultima_visual = models.DateTimeField(blank=True, null=True, verbose_name="Data ultima apertura del video")
    data_completamento = models.DateTimeField(blank=True, null=True, verbose_name="Data completamento video")
    totale_secondi_visualizzati = models.IntegerField(blank=True, null=True, default=0, verbose_name="Totale secondi visualizzati")

    def __str__(self):
        return f"{self.utente}-{self.video_corso}"
    
    def percentuale_completamento(self):
        if self.video_corso.durata_video and self.video_corso.durata_video > 0:
            return round((self.totale_secondi_visualizzati / self.video_corso.durata_video) * 100, 2)
        else:
            return 0

    class Meta:
        unique_together = (("utente", "video_corso"),)
        verbose_name_plural = "Stati Video"
        verbose_name = "Stato Video"

class AttestatiVideo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    utente = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name="Utente")
    # video_corso = models.ForeignKey(VideoCorso, null=True, on_delete=models.SET_NULL, verbose_name="Video Corso")
    corso = models.ForeignKey(Corso, null=True, on_delete=models.SET_NULL, verbose_name="Corso")
    data_conseguimento = models.DateTimeField(blank=True, null=True, verbose_name="Data conseguimento")
    data_download = models.DateTimeField(blank=True, null=True, verbose_name="Data download")
    pdf = models.FileField(blank=True, null=True, upload_to="attestati/")
    
    def __str__(self):
        return f"{self.utente.username} - {self.corso.titolo}"
    
    class Meta:
        verbose_name = "Attestato Video"
        verbose_name_plural = "Attestati Video"

class Quiz(models.Model):
    # video_corso = models.ForeignKey(VideoCorso, on_delete=models.CASCADE, related_name="quiz")
    corso = models.ForeignKey(Corso, blank=True, null=True, on_delete=models.CASCADE, related_name="quiz")
    titolo = models.CharField(max_length=255)

    def __str__(self):
        return self.titolo
    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"

class Domanda(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="domande")
    testo = models.TextField()

    def __str__(self):
        return self.testo
    
    class Meta:
        verbose_name = "Domanda"
        verbose_name_plural = "Domande"

class OpzioneRisposta(models.Model):
    domanda = models.ForeignKey(Domanda, on_delete=models.CASCADE, related_name="opzioni")
    testo_opzione = models.TextField()
    corretta = models.BooleanField(default=False)

    def __str__(self):
        return self.testo_opzione
    
    class Meta:
        verbose_name = "OpzioneRisposta"
        verbose_name_plural = "Opzioni Risposta"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    risultati = JSONField(default=dict)

    def __str__(self):
        return f"{self.user} - {self.quiz.corso}"

    class Meta:
        verbose_name = "Tentativo Quiz"
        verbose_name_plural = "Tentativi Quiz"
