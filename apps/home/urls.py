# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from apps.home import views
from custom_mail.views import *
from .views import *

urlpatterns = [

    # Pagine amministratore
    path('', views.index, name='home'),
    path("amministrazione/dashboard/", AmministrazioneView.as_view(), name="amministrazione"),
    path("amministrazione/aziende/", AziendeView.as_view(), name="aziende"),
    path("amministrazione/aggiungi_azienda/", AggiungiAziendaView.as_view(), name="aggiungi_azienda"),
    path("amministrazione/azienda/<int:id_azienda>/", AziendeView.as_view(), name="aziende"),
    path("amministrazione/azienda/<int:id_azienda>/dettaglio", DettagliAziendaView.as_view(), name="dettagli_azienda"),
    path("amministrazione/lista_utenti/", UtentiView.as_view(), name="lista_utenti"),
    path("amministrazione/caricavideocorsi/", UploadVideoCorsiView.as_view(), name="caricavideocorsi"),
    path("amministrazione/aggiungi_corso/", AggiungiCorsoView.as_view(), name="aggiungi_corso"),
    path("amministrazione/aggiungi_utente/", AggiungiUtenteView.as_view(), name="aggiungi_utente"),
    path("amministrazione/mail/", SentMailListView.as_view(), name="sent_mail_list"),
    path("amministrazione/mail/<int:id>/", SentMailView.as_view(), name="sent_mail_detail"),
    path("amministrazione/corso/<int:id_corso>/configura_moduli", ConfiguraModuliView.as_view(), name="configura_moduli"),
    path("amministrazione/corso/<int:id_corso>/crea_quiz", CreaQuizView.as_view(), name="crea_quiz"),

    # Pagine utente
    path("utente/pagina_profilo/<int:id_utente>", ProfiloView.as_view(), name="utente_profilo"),
    path("utente/corsi/", CorsiView.as_view(), name="utente_corsi"),
    path("utente/corso/<int:id_corso>/dettagli", DettagliCorsoView.as_view(), name="utente_corso_dettaglio"),
    path("utente/corso/<int:id_corso>/videocorsi", VideoCorsiView.as_view(), name="videocorsi"), 
    path("utente/corso/<int:id_corso>/quiz", QuizView.as_view(), name="quiz"),
    path('risultati_quiz/<int:id_corso>/<int:id_quiz_attempt>/', QuizRisultatiView.as_view(), name='risultati_quiz'),
    path('salva-modulo/<int:id_corso>/', SalvaModuloView.as_view(), name='salva_modulo'),
    path('ordina-videocorsi/<int:id_corso>/', OrdinaVideocorsiView.as_view(), name='ordina_videocorsi'),


    #scarica attestato
    path('scarica_attestato/<int:id_corso>/', scarica_attestato, name='scarica_attestato'),

    path("utente/attestati/", AttestatiView.as_view(), name="utente_attestati"),
    
    # Pagine videocorso
    path("utente/videocorso/<int:id_video>/", WatchVideoCorsoView.as_view(), name="video_corso_utente"),
    
    # Pagine di servizio
    path("supporto/", SupportoView.as_view(), name="supporto"),

]
