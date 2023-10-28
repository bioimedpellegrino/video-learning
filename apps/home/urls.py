# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import *

urlpatterns = [

    # Pagine amministratore
    path('', views.index, name='home'),
    path("amministrazione/dashboard/", AmministrazioneView.as_view(), name="amministrazione"),
    path("amministrazione/aziende/", AziendeView.as_view(), name="aziende"),
    path("amministrazione/azienda/<int:id_azienda>/", AziendeView.as_view(), name="aziende"),
    path("amministrazione/lista_utenti/", UtentiView.as_view(), name="lista_utenti"),
    path("amministrazione/videocorsi/", VideoCorsiView.as_view(), name="videocorsi"),
    path("amministrazione/caricavideocorsi/", UploadVideoCorsiView.as_view(), name="caricavideocorsi"),
    path("amministrazione/aggiungi_corso/", AggiungiCorsoView.as_view(), name="aggiungi_corso"),
    path("amministrazione/aggiungi_azienda/", AggiungiAziendaView.as_view(), name="aggiungi_azienda"),
    path("amministrazione/aggiungi_utente/", AggiungiUtenteView.as_view(), name="aggiungi_utente"),

    # Pagine utente
    path("utente/profilo/", ProfiloView.as_view(), name="utente_profilo"),
    path("utente/corsi/", CorsiView.as_view(), name="utente_corsi"),
    path("utente/attestati/", AttestatiView.as_view(), name="utente_attestati"),
    
    # Pagine di servizio
    path("supporto/", SupportoView.as_view(), name="supporto"),
    
    # Qualunque altro path non valido viene gestito dalla vista error_pages
    re_path(r'^.*\.*', views.error_pages, name='error_pages'),

]
