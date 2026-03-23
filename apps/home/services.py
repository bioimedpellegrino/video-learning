import json

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Azienda, Corso, CustomUser, VideoCorso


def build_admin_course_detail_context(corso):
    aziende_corso = corso.aziende.all()
    videocorsi_corso = corso.video_corsi.all()
    docenti_corso = corso.docenti.all()

    return {
        'segment': 'utente_corso_dettaglio',
        'aziende_non_aggiunte': Azienda.objects.exclude(id__in=aziende_corso.values_list('id', flat=True)),
        'aziende_corso': aziende_corso,
        'videocorsi_non_aggiunti': VideoCorso.objects.exclude(id__in=videocorsi_corso.values_list('id', flat=True)),
        'videocorsi_corso': videocorsi_corso,
        'docenti_non_aggiunti': CustomUser.objects.filter(user__is_staff=True).exclude(
            id__in=docenti_corso.values_list('id', flat=True)
        ),
        'docenti_corso': docenti_corso,
        'corso': corso,
        'svolgimento_esame': False,
    }


def parse_video_order(raw_order):
    if not raw_order:
        return []

    try:
        return json.loads(raw_order)
    except (TypeError, json.JSONDecodeError):
        return []


def apply_video_order(corso, raw_order):
    parsed_order = parse_video_order(raw_order)
    allowed_ids = set(corso.video_corsi.values_list('id', flat=True))

    for item in parsed_order:
        video_id = item.get('id')
        new_order = item.get('order')
        if video_id not in allowed_ids:
            continue
        VideoCorso.objects.filter(pk=video_id).update(ordine=new_order)


@transaction.atomic
def sync_course_configuration(corso, azienda_ids, videocorso_ids, docente_ids, raw_order=None):
    aziende = Azienda.objects.filter(pk__in=azienda_ids)
    videocorsi = VideoCorso.objects.filter(pk__in=videocorso_ids)
    docenti = CustomUser.objects.filter(pk__in=docente_ids, user__is_staff=True)

    corso.aziende.set(aziende)
    corso.video_corsi.set(videocorsi)
    corso.docenti.set(docenti)

    current_aziende = list(corso.aziende.all())
    for videocorso in corso.video_corsi.all():
        videocorso.corso = corso
        videocorso.save(update_fields=['corso'])
        videocorso.aziende.set(current_aziende)

    apply_video_order(corso, raw_order)

    return corso


@transaction.atomic
def create_course_module(corso, *, titolo, descrizione, ordine, video_file, poster_file, external_url):
    videocorso = VideoCorso(
        titolo=titolo,
        descrizione=descrizione,
        ordine=ordine,
        corso=corso,
        video_file=video_file,
        poster_file=poster_file,
        external_url=external_url,
    )

    try:
        videocorso.full_clean()
    except ValidationError:
        raise

    videocorso.save()
    videocorso.aziende.set(corso.aziende.all())
    return videocorso


@transaction.atomic
def update_course_module(videocorso, *, titolo, descrizione, ordine, video_file, poster_file, external_url):
    videocorso.titolo = titolo
    videocorso.descrizione = descrizione
    videocorso.ordine = ordine
    videocorso.external_url = external_url

    if video_file:
        videocorso.video_file = video_file
    if poster_file:
        videocorso.poster_file = poster_file

    videocorso.full_clean()
    videocorso.save()
    if videocorso.corso_id:
        videocorso.aziende.set(videocorso.corso.aziende.all())
    return videocorso
