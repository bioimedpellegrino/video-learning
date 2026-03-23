# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.home.models import (
    Azienda,
    Corso,
    CustomUser,
    Domanda,
    OpzioneRisposta,
    Quiz,
    QuizAttempt,
    VideoCorso,
)
from apps.home.services import apply_video_order, create_course_module, sync_course_configuration


class AccessControlTests(TestCase):
    def setUp(self):
        self.azienda_a = Azienda.objects.create(nome="Azienda A")
        self.azienda_b = Azienda.objects.create(nome="Azienda B")
        self.corso = Corso.objects.create(titolo="Corso Sicurezza")
        self.corso.aziende.add(self.azienda_a)

        self.video_1 = VideoCorso.objects.create(titolo="Modulo 1", ordine=1, corso=self.corso)
        self.video_1.aziende.add(self.azienda_a)

        self.student_user = User.objects.create_user(username="student", password="testpass123")
        self.student_profile = CustomUser.objects.create(user=self.student_user, azienda=self.azienda_a)

        self.other_user = User.objects.create_user(username="other", password="testpass123")
        self.other_profile = CustomUser.objects.create(user=self.other_user, azienda=self.azienda_b)

        self.quiz = Quiz.objects.create(corso=self.corso, titolo="Quiz finale")
        self.domanda = Domanda.objects.create(quiz=self.quiz, testo="Domanda 1")
        self.correct_option = OpzioneRisposta.objects.create(
            domanda=self.domanda,
            testo_opzione="Corretta",
            corretta=True,
        )
        self.wrong_option = OpzioneRisposta.objects.create(
            domanda=self.domanda,
            testo_opzione="Errata",
            corretta=False,
        )

    def test_video_page_is_blocked_for_user_from_other_company(self):
        self.client.login(username="other", password="testpass123")

        response = self.client.get(reverse("video_corso_utente", args=[self.video_1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/page-404.html")

    def test_quiz_attempt_results_are_private_to_owner(self):
        attempt = QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            risultati={
                str(self.domanda.id): {
                    "risultato": True,
                    "risposta_data": self.correct_option.id,
                    "testo_risposta": self.correct_option.testo_opzione,
                }
            },
        )

        self.client.login(username="other", password="testpass123")
        response = self.client.get(reverse("risultati_quiz", args=[self.corso.id, attempt.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/page-404.html")

    def test_quiz_requires_authenticated_user(self):
        response = self.client.get(reverse("quiz", args=[self.corso.id]))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class CourseServiceTests(TestCase):
    def setUp(self):
        self.azienda_a = Azienda.objects.create(nome="Azienda A")
        self.azienda_b = Azienda.objects.create(nome="Azienda B")
        self.corso = Corso.objects.create(titolo="Corso 1")

        self.docente_user = User.objects.create_user(username="teacher", password="testpass123", is_staff=True)
        self.docente = CustomUser.objects.create(user=self.docente_user, azienda=self.azienda_a)

        self.video_a = VideoCorso.objects.create(titolo="Video A", ordine=1)
        self.video_b = VideoCorso.objects.create(titolo="Video B", ordine=2)

    def test_sync_course_configuration_updates_relations_consistently(self):
        sync_course_configuration(
            self.corso,
            azienda_ids=[str(self.azienda_a.id), str(self.azienda_b.id)],
            videocorso_ids=[str(self.video_a.id), str(self.video_b.id)],
            docente_ids=[str(self.docente.id)],
            raw_order='[{"id": %s, "order": 2}, {"id": %s, "order": 1}]' % (self.video_a.id, self.video_b.id),
        )

        self.assertCountEqual(self.corso.aziende.values_list("id", flat=True), [self.azienda_a.id, self.azienda_b.id])
        self.assertCountEqual(self.corso.docenti.values_list("id", flat=True), [self.docente.id])
        self.assertCountEqual(self.corso.video_corsi.values_list("id", flat=True), [self.video_a.id, self.video_b.id])

        self.video_a.refresh_from_db()
        self.video_b.refresh_from_db()
        self.assertEqual(self.video_a.corso_id, self.corso.id)
        self.assertEqual(self.video_b.corso_id, self.corso.id)
        self.assertCountEqual(self.video_a.aziende.values_list("id", flat=True), [self.azienda_a.id, self.azienda_b.id])
        self.assertEqual(self.video_a.ordine, 2)
        self.assertEqual(self.video_b.ordine, 1)

    def test_create_course_module_inherits_course_companies(self):
        self.corso.aziende.add(self.azienda_a)

        module = create_course_module(
            self.corso,
            titolo="Nuovo modulo",
            descrizione="Descrizione",
            ordine=3,
            video_file=None,
            poster_file=None,
            external_url="https://cdn.example.com/video.mp4",
        )

        self.assertEqual(module.corso_id, self.corso.id)
        self.assertCountEqual(module.aziende.values_list("id", flat=True), [self.azienda_a.id])

    def test_apply_video_order_ignores_unknown_video_ids(self):
        self.corso.video_corsi.add(self.video_a)
        other_video = VideoCorso.objects.create(titolo="Altro", ordine=5)

        apply_video_order(
            self.corso,
            '[{"id": %s, "order": 7}, {"id": %s, "order": 1}]' % (self.video_a.id, other_video.id),
        )

        self.video_a.refresh_from_db()
        other_video.refresh_from_db()
        self.assertEqual(self.video_a.ordine, 7)
        self.assertEqual(other_video.ordine, 5)


class ModuleManagementTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            password="testpass123",
            email="admin@example.com",
        )
        self.azienda = Azienda.objects.create(nome="Azienda Demo")
        self.corso = Corso.objects.create(titolo="Informatica")
        self.corso.aziende.add(self.azienda)
        self.videocorso = VideoCorso.objects.create(
            titolo="Hardware base",
            descrizione="Introduzione ai componenti",
            ordine=1,
            corso=self.corso,
            external_url="https://cdn.example.com/hardware.mp4",
        )
        self.videocorso.aziende.add(self.azienda)

    def test_superuser_can_update_existing_module(self):
        self.client.login(username="admin_test", password="testpass123")

        response = self.client.post(
            reverse("modifica_modulo", args=[self.videocorso.id]),
            {
                "titolo": "Fondamenti di informatica",
                "descrizione": "Panoramica aggiornata del modulo",
                "ordine": 2,
                "external_url": "https://cdn.example.com/fondamenti.mp4",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.videocorso.refresh_from_db()
        self.assertEqual(self.videocorso.titolo, "Fondamenti di informatica")
        self.assertEqual(self.videocorso.descrizione, "Panoramica aggiornata del modulo")
        self.assertEqual(self.videocorso.ordine, 2)
        self.assertEqual(self.videocorso.external_url, "https://cdn.example.com/fondamenti.mp4")
        self.assertCountEqual(self.videocorso.aziende.values_list("id", flat=True), [self.azienda.id])
