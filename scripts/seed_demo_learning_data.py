import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.contrib.auth.models import User

from apps.home.models import Azienda, Corso, CustomUser, VideoCorso


PASSWORD = "asd"

COMPANIES = [
    {
        "name": "GreenByte Solutions",
        "users": [
            ("g.martini", "Giulia", "Martini", "giulia.martini@greenbyte.local"),
            ("l.rossi", "Luca", "Rossi", "luca.rossi@greenbyte.local"),
        ],
    },
    {
        "name": "NordData Formazione",
        "users": [
            ("m.conti", "Marta", "Conti", "marta.conti@norddata.local"),
            ("a.ricci", "Andrea", "Ricci", "andrea.ricci@norddata.local"),
        ],
    },
    {
        "name": "Studio Informatica 360",
        "users": [
            ("s.gallo", "Sara", "Gallo", "sara.gallo@studio360.local"),
            ("f.longo", "Fabio", "Longo", "fabio.longo@studio360.local"),
        ],
    },
]

COURSE_TITLE = "Informatica"
COURSE_DESCRIPTION = (
    "Percorso introduttivo ai concetti chiave dell'informatica: hardware, sistemi operativi, "
    "produttivita personale, reti, sicurezza e servizi cloud."
)

MODULES = [
    {
        "title": "Introduzione all'hardware e al software",
        "description": "Panoramica su componenti del PC, periferiche, software di base e differenze tra sistema operativo e applicazioni.",
        "order": 1,
        "external_url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    },
    {
        "title": "Sistemi operativi e gestione dei file",
        "description": "Organizzare cartelle e documenti, usare in modo corretto il sistema operativo e lavorare con le impostazioni essenziali.",
        "order": 2,
        "external_url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    },
    {
        "title": "Produttivita digitale e strumenti da ufficio",
        "description": "Uso quotidiano di editor di testo, fogli di calcolo, presentazioni e buone pratiche di collaborazione digitale.",
        "order": 3,
        "external_url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    },
    {
        "title": "Reti, internet e servizi online",
        "description": "Concetti base di rete, navigazione web, posta elettronica, cloud e strumenti online per il lavoro.",
        "order": 4,
        "external_url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    },
    {
        "title": "Sicurezza informatica di base",
        "description": "Password sicure, phishing, backup, aggiornamenti, antivirus e comportamenti corretti per proteggere dati e dispositivi.",
        "order": 5,
        "external_url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    },
]


def ensure_user(username, first_name, last_name, email, azienda, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "is_staff": is_staff,
            "is_superuser": False,
        },
    )

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.is_staff = is_staff
    user.set_password(PASSWORD)
    user.save()

    profile, _ = CustomUser.objects.get_or_create(
        user=user,
        defaults={"azienda": azienda},
    )
    profile.azienda = azienda
    profile.save()

    return user, profile, created


def ensure_course(aziende, docente_profile):
    corso, created = Corso.objects.get_or_create(
        titolo=COURSE_TITLE,
        defaults={"descrizione": COURSE_DESCRIPTION},
    )
    corso.descrizione = COURSE_DESCRIPTION
    corso.save()
    corso.aziende.set(aziende)
    corso.docenti.add(docente_profile)
    return corso, created


def ensure_modules(corso, aziende):
    created_count = 0
    updated_count = 0

    for module in MODULES:
        videocorso, created = VideoCorso.objects.get_or_create(
            corso=corso,
            titolo=module["title"],
            defaults={
                "descrizione": module["description"],
                "ordine": module["order"],
                "external_url": module["external_url"],
            },
        )

        videocorso.descrizione = module["description"]
        videocorso.ordine = module["order"]
        videocorso.external_url = module["external_url"]
        videocorso.corso = corso
        videocorso.save()
        videocorso.aziende.set(aziende)

        if created:
            created_count += 1
        else:
            updated_count += 1

    return created_count, updated_count


def main():
    created_companies = 0
    created_users = 0

    aziende = []
    for company_data in COMPANIES:
        azienda, company_created = Azienda.objects.get_or_create(nome=company_data["name"])
        aziende.append(azienda)
        if company_created:
            created_companies += 1

        for username, first_name, last_name, email in company_data["users"]:
            _, _, user_created = ensure_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                azienda=azienda,
                is_staff=False,
            )
            if user_created:
                created_users += 1

    docente_user, docente_profile, docente_created = ensure_user(
        username="docente.informatica",
        first_name="Davide",
        last_name="Bianchi",
        email="docente.informatica@videolearning.local",
        azienda=aziende[0],
        is_staff=True,
    )
    if docente_created:
        created_users += 1

    corso, course_created = ensure_course(aziende, docente_profile)
    module_created, module_updated = ensure_modules(corso, aziende)

    print("Seed completato")
    print(f"Aziende create: {created_companies}")
    print(f"Nuovi utenti creati: {created_users}")
    print(f"Corso {'creato' if course_created else 'aggiornato'}: {corso.titolo}")
    print(f"Docente: {docente_user.username} / password: {PASSWORD}")
    print(f"Moduli creati: {module_created}")
    print(f"Moduli aggiornati: {module_updated}")
    print("Password impostata a 'asd' per tutti gli utenti seed.")


if __name__ == "__main__":
    main()
