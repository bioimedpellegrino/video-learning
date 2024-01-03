from django import template
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from custom_mail.models import Mail
from django.shortcuts import redirect, render
from django.views.generic import View
from django.db import IntegrityError
from .forms import *
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import json
import os

import datetime

@login_required(login_url="/login/")
def index(request):
    
    context = {'segment': 'index','breadcrumb_level_1': 'Home'}
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('amministrazione'))
    else:
        return HttpResponseRedirect(reverse('utente_corsi'))


@login_required(login_url="/login/")
def error_pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
    
class HomePageView(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            video_corsi = VideoCorso.objects.all()
            stati_video = None
            azienda = None
            return render(request, self.template_name, 
                    {
                    'video_corsi': video_corsi,
                    'stati_video': stati_video,
                    'azienda': azienda,
                    })
        if request.user.is_authenticated:
            custom_user = request.user.customuser
            azienda = custom_user.azienda
            video_corsi = VideoCorso.objects.filter(azienda=azienda)
            stati_video = StatoVideo.objects.filter(utente=custom_user)
        else:
            azienda = None
            video_corsi = None
            stati_video = None

        context = {
            'video_corsi': video_corsi,
            'stati_video': stati_video,
            'azienda': azienda,
        }
        return render(request, self.template_name, context)

class AziendeView(View):
    template_name = 'home/aziende.html'
    context = {'segment': 'amministrazione-aziende', 'breadcrumb_level_1': 'Amministrazione', 'breadcrumb_level_2': 'Aziende'}

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            aziende = Azienda.objects.all()
            self.context["aziende"] = aziende
            return render(request, self.template_name, self.context)
        profile = CustomUser.objects.get(user=request.user)
        aziende = profile.aziende.all()
        utenti = CustomUser.objects.filter(azienda__isnull=True)
        self.context["aziende"] = aziende
        self.context["utenti"] = utenti
        
        return render(request, self.template_name, self.context)

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        profile = CustomUser.objects.get(user=request.user)

        try:
            nome_azienda = request.POST.get('nome_azienda')
            utenti_selezionati = request.POST.getlist('utenti_selezionabili')

            if nome_azienda and utenti_selezionati:
                new_azienda, _ = Azienda.objects.get_or_create(nome=nome_azienda)
                new_azienda.staff_users.add(profile)
                utenti = CustomUser.objects.filter(pk__in=utenti_selezionati)
                utenti.update(azienda=new_azienda)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.context["error"] = "Ops! Si è verificato un'errore."
        
        return redirect('aziende')

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def delete(self, request, *args, **kwargs):
        
        profile = CustomUser.objects.get(user=request.user)
        azienda = Azienda.objects.get(pk=kwargs.get("id_azienda"))
        if profile in azienda.staff_users.all():
            azienda.delete()
            return HttpResponse({"message": "ok", "status": 200})
        else:
            return HttpResponse({"message": "ko", "status": 403})
        
from django.shortcuts import get_object_or_404

class DettagliAziendaView(View):
    template_name = 'home/dettagli-azienda.html'
    context = {'segment': 'amministrazione-aziende', 'breadcrumb_level_1': 'Amministrazione', 'breadcrumb_level_2': 'Aziende'}


    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        azienda_id = kwargs.get('id_azienda')
        azienda = get_object_or_404(Azienda, id=azienda_id)
        utenti_azienda = azienda.utenti.all()
        utenti_no_azienda = CustomUser.objects.filter(azienda__isnull=True)

        context = {
            'segment': 'amministrazione-aziende', 
            'breadcrumb_level_1': 'Amministrazione', 
            'breadcrumb_level_2': 'Aziende',
            'breadcrumb_level_3': 'Dettaglio azienda',
            'azienda': azienda,
            'utenti_azienda': utenti_azienda,
            'utenti_no_azienda': utenti_no_azienda,
        }

        return render(request, self.template_name, context)

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        azienda_id = kwargs.get('id_azienda')
        azienda = get_object_or_404(Azienda, id=azienda_id)
        utenti_associati = request.POST.getlist('utenti_associati')
        utenti_disponibili = request.POST.getlist('utenti_disponibili')
        
        if utenti_associati:
            utenti = CustomUser.objects.filter(pk__in=utenti_associati)
            utenti.update(azienda=azienda)
        
        if utenti_disponibili:
            utenti = CustomUser.objects.filter(pk__in=utenti_disponibili)
            utenti.update(azienda=None)

        context = {
            'segment': 'amministrazione-aziende', 
            'breadcrumb_level_1': 'Amministrazione', 
            'breadcrumb_level_2': 'Aziende',
            'breadcrumb_level_3': 'Dettaglio azienda',
            'azienda': azienda,
            'utenti_azienda': azienda.utenti.all(),
            'utenti_no_azienda': CustomUser.objects.filter(azienda__isnull=True),
        }

        return redirect('dettagli_azienda', id_azienda=azienda_id)

# Per adesso creo solo il nome dell'azienda e lascio la lista utenti da aggiungere vuota perchè associo l'azienda unica già in fase di creazione utente
# Se per il futuro un utente potrà avere più di una azienda associata potremo usare questa view e modificare il campo azienda di CustomUser 
# con ManyToManyField
class AggiungiAziendaView(View):
    template_name = 'home/aggiungi-azienda.html'
    context = {'segment': 'amministrazione-aziende', 'breadcrumb_level_1': 'Amministrazione', 'breadcrumb_level_2': 'Aziende', 'breadcrumb_level_3': 'Aggiungi azienda'}

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-aziende'}
        if request.user.is_superuser:
            # Utenti senza azienda ancora associata
            utenti = CustomUser.objects.filter(azienda__isnull=True)
            context["utenti"] = utenti
            return render(request, self.template_name, context)
        
    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        try:
            nome_azienda = request.POST.get('nome_azienda')
            utenti_selezionati = request.POST.getlist('utenti')

            if nome_azienda:
                # Crea o ottiene un'azienda con il nome specificato
                azienda, created = Azienda.objects.get_or_create(nome=nome_azienda)

                if utenti_selezionati:
                    # Associa gli utenti selezionati all'azienda
                    utenti = CustomUser.objects.filter(pk__in=utenti_selezionati)
                    azienda.staff_users.set(utenti)

        except Exception as e:
            # Gestione dell'errore
            import traceback
            traceback.print_exc()
            self.context["error"] = "Ops! Si è verificato un'errore."
        
        return redirect('aziende')
        

class UtentiView(View):
    template_name = 'home/utenti.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = {
                'segment': 'amministrazione-utenti-lista',
                'breadcrumb_level_1': 'Amministrazione', 
                'breadcrumb_level_2': 'Utenti', 
                'breadcrumb_level_3': 'Lista utenti'
                
            }
        if request.user.is_superuser:
            utenti = CustomUser.objects.all()
            context["utenti"] = utenti
            return render(request, self.template_name, context)
        profile = CustomUser.objects.get(user=request.user)
        utenti = CustomUser.objects.filter(azienda=profile.azienda)
        context["utenti"] = utenti
        #nell' html voglio riferirmi al nome dell'utente usando la foreign key user
        
        
        return render(request, self.template_name, context)


class VideoCorsiView(View):
    template_name = 'home/video-corsi.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            context = { 'segment' : 'amministrazione-videocorsi'}
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            videocorsi = list(corso.video_corsi.all().order_by('ordine'))
            context["videocorsi"] = videocorsi
            context["corso"] = corso
            return render(request, self.template_name, context)
        else:
            context = { 'segment' : 'amministrazione-videocorsi'}
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            utente = CustomUser.objects.get(user=request.user)        
            videocorsi = list(corso.video_corsi.all().order_by('ordine'))
            stati_video = StatoVideo.objects.filter(video_corso__in=videocorsi, utente=utente)
            # Devo controllare se il video corso è stato completato dall'utente altrimenti disabilito il pulsante dei corsi successivi
            for i in range(len(videocorsi)):
                if i == 0:
                    videocorsi[i].prev_completed = True
                    continue
                prev_videocorso = videocorsi[i-1]
                prev_stato_video = stati_video.filter(video_corso=prev_videocorso).first()
                if prev_stato_video:
                    videocorsi[i].prev_completed = prev_stato_video.completato
                else:
                    videocorsi[i].prev_completed = False

            context["videocorsi"] = videocorsi
            context["corso"] = corso
            return render(request, self.template_name, context)

class UploadVideoCorsiView(View):
    template_name = 'home/uploadcorsi.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-uploadcorsi'}
        #TODO
        return render(request, self.template_name, context)
    
    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-uploadcorsi'}
        #TODO
        return render(request, self.template_name, context)

class ProfiloView(View):
    template_name = 'home/utente_profilo.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'utente_profilo'}
        user_id = kwargs.get('id_utente')
        is_admin = False
        if request.user.username == 'admin' and user_id == request.user.id:
            return redirect('amministrazione')
        elif request.user.username == 'admin' and user_id != request.user.id:
            is_admin = True

        utente = CustomUser.objects.get(id=user_id)
        azienda = utente.azienda
        video_corsi = azienda.video_corsi.all()

        # gli stati video relativi all'utente   
        stati_video_utente = StatoVideo.objects.filter(video_corso__in=video_corsi, utente=utente)
        video_corsi_utente = {video_corso: (video_corso, StatoVideo.objects.filter(video_corso=video_corso, utente=utente).first(), StatoVideo.objects.filter(video_corso=video_corso, utente=utente).exists()) for video_corso in video_corsi}        
        context = { 'segment' : 'utente_profilo',
                    'utente': utente,
                    'is_admin': is_admin,
                    'video_corsi_utente': video_corsi_utente,
                    'stati_video': stati_video_utente,
                    'azienda': azienda,
                   }
        return render(request, self.template_name, context)
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'utente_profilo'}
        #TODO
        return render(request, self.template_name, context)

class CorsiView(View):
    template_name = 'home/utente_corsi.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            context = { 'segment' : 'utente_corsi'}
            if request.user.is_staff:       
                # i corsi di cui l'utente è docente
                corsi = Corso.objects.filter(docenti__user=request.user)
                context["corsi"] = corsi
                return render(request, self.template_name, context)
             
            # Se l'utente non è docente deve avere corsi specifici e non tutti quelli dell'azienda uso var video_corsi_spec
            corsi = Corso.objects.filter(aziende=request.user.customuser.azienda)
            context["corsi"] = corsi
            return render(request, self.template_name, context)
        else:
            return redirect('amministrazione')

    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            context = { 'segment' : 'utente_corsi'}
            return render(request, self.template_name, context)
        else:
            return redirect('amministrazione')

# Dettaglio corso deve essere accessibile solo dall'admin e deve avere i dati relativi al corso
class DettagliCorsoView(View):
    template_name = 'home/utente_corso_dettagli.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            corso_completato = False
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            aziende_all = Azienda.objects.all()
            aziende_corso = corso.aziende.all()
            aziende_non_aggiunte = aziende_all.exclude(id__in=aziende_corso.values_list('id', flat=True))
            # video corsi
            videocorsi = VideoCorso.objects.all()
            videocorsi_non_aggiunti = videocorsi.exclude(id__in=corso.video_corsi.values_list('id', flat=True))
            docenti = CustomUser.objects.filter(user__is_staff=True)
            docenti_non_aggiunti = docenti.exclude(id__in=corso.docenti.values_list('id', flat=True))
            
            context = {
                'segment' : 'utente_corso_dettaglio',
                'aziende_non_aggiunte': aziende_non_aggiunte,
                'aziende_corso': aziende_corso,
                'videocorsi_non_aggiunti': videocorsi_non_aggiunti,
                'videocorsi_corso': corso.video_corsi.all(),
                'docenti_non_aggiunti': docenti_non_aggiunti,
                'docenti_corso': corso.docenti.all(),
                'corso': corso,
                'svolgimento_esame': corso_completato,
            }
            return render(request, self.template_name, context)
        else:
            corso_completato = False
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            utente = CustomUser.objects.get(user=request.user)
            aziende_all = Azienda.objects.all()
            aziende_corso = corso.aziende.all()
            stati_video = StatoVideo.objects.filter(video_corso__in=corso.video_corsi.all(), utente=utente)
            azienda_utente = utente.azienda
            videocorsi = corso.video_corsi.all()
            # vedere se per ogni video corso associato al corso l'utente ha completato il video
            
            # se tutti gli stati_video hanno il campo completato a true allora il corso è completato
            if stati_video and all([stato_video.completato for stato_video in stati_video]) and len(stati_video) == len(videocorsi):
                corso_completato = True

            context = {
                'segment' : 'utente_corso_dettaglio',
                'aziende_corso': aziende_corso,
                'corso': corso,
                'corso_completato': corso_completato,
            }
            return render(request, self.template_name, context)

    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        corso = Corso.objects.get(pk=kwargs.get('id_corso'))
        utenti = CustomUser.objects.all()
        aziende_all = Azienda.objects.all()
        id_aziende_aggiunte = request.POST.getlist('aziende')
        aziende_corso = corso.aziende.all()
        aziende_non_aggiunte = aziende_all.exclude(id__in=aziende_corso.values_list('id', flat=True))
        videocorsi = VideoCorso.objects.all()
        videocorsi_non_aggiunti = videocorsi.exclude(id__in=corso.video_corsi.values_list('id', flat=True))
        docenti = CustomUser.objects.filter(user__is_staff=True)
        docenti_non_aggiunti = docenti.exclude(id__in=corso.docenti.values_list('id', flat=True))

        for id_azienda in id_aziende_aggiunte:
            azienda = Azienda.objects.get(pk=id_azienda)
            if azienda not in corso.aziende.all():
                corso.aziende.add(azienda)
        for azienda in corso.aziende.all():
            if str(azienda.id) not in id_aziende_aggiunte:
                corso.aziende.remove(azienda)
        aziende_corso = corso.aziende.all()      

        # aggiungere o rimuovere i videocorsi al corso
        id_videocorsi_aggiunti = request.POST.getlist('videocorsi')
        for id_videocorso in id_videocorsi_aggiunti:
            videocorso = VideoCorso.objects.get(pk=id_videocorso)
            if videocorso not in corso.video_corsi.all():
                corso.video_corsi.add(videocorso)
        for videocorso in corso.video_corsi.all():
            if str(videocorso.id) not in id_videocorsi_aggiunti:
                corso.video_corsi.remove(videocorso)
        videocorsi_corso = corso.video_corsi.all()

        # Aggiorno il campo aziende dei videocorsi associati al corso per le aziende aggiunte
        for videocorso in corso.video_corsi.all():
            for azienda in aziende_corso:
                if azienda not in videocorso.aziende.all():
                    videocorso.aziende.add(azienda)
            for azienda in videocorso.aziende.all():
                if azienda not in aziende_corso:
                    videocorso.aziende.remove(azienda)

        # aggiungere o rimuovere i docenti al corso
        id_docenti_aggiunti = request.POST.getlist('docenti')
        for id_docente in id_docenti_aggiunti:
            docente = CustomUser.objects.get(pk=id_docente)
            if docente not in corso.docenti.all():
                corso.docenti.add(docente)
        for docente in corso.docenti.all():
            if str(docente.id) not in id_docenti_aggiunti:
                corso.docenti.remove(docente)
        docenti_corso = corso.docenti.all()

        #  Aggiorno ordine dei videocorsi
        try:
            new_order = json.loads(request.POST.get('order'))
            for item in new_order:
                videocorso = VideoCorso.objects.get(pk=item['id'])
                videocorso.ordine = item['order']
                videocorso.save()
        except Exception as e:
            print(e)
            pass

        context = {
            'segment' : 'utente_corso_dettaglio',
            'aziende_non_aggiunte': aziende_non_aggiunte,
            'aziende_corso': aziende_corso,
            'videocorsi_non_aggiunti': videocorsi_non_aggiunti,
            'videocorsi_corso': videocorsi_corso,
            'docenti_non_aggiunti': docenti_non_aggiunti,
            'docenti_corso': docenti_corso,
            'corso': corso,
        }
        return render(request, self.template_name, context)

class WatchVideoCorsoView(View):
    template_name = 'home/watch-video.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'miei_corsi'}
        id_video = kwargs.get('id_video')
        custom_user = CustomUser.objects.get(user=request.user)
        video_corso = VideoCorso.objects.get(pk=id_video)
        # il corso a cui è associato il videocorso
        corso = video_corso.corso

        if video_corso.ordine > 1:
            video_corso_precedente = VideoCorso.objects.get(ordine=video_corso.ordine - 1)
            stato_precedente = StatoVideo.objects.filter(utente=custom_user, video_corso=video_corso_precedente, completato=True).exists()
            if not stato_precedente:
                return render(request, 'home/page-404.html')

        try:
            video_corso = VideoCorso.objects.get(pk=id_video)
            context['breadcrumb_level_1'] = video_corso.titolo
        except VideoCorso.DoesNotExist:
            return render(request, 'home/page-404.html')
        
        else:
            stato_video, _ = StatoVideo.objects.get_or_create(utente=custom_user, video_corso=video_corso)
            context["video_corso"] = video_corso
            context["custom_user"] = custom_user
            context["stato_video"] = stato_video
            context["corso"] = corso
            return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        
        id_video = kwargs.get('id_video')
        custom_user = CustomUser.objects.get(user=request.user)
        
        try:
            video_corso = VideoCorso.objects.get(pk=id_video)
        except VideoCorso.DoesNotExist:
            return HttpResponse({"message": "Video non trovato", "status": 404})
        
        if not custom_user.azienda in video_corso.aziende.all():
            return HttpResponse({"message": "Non autorizzato", "status": 403})
        
        try:
            stato_video = StatoVideo.objects.get(utente=custom_user, video_corso=video_corso)
        except StatoVideo.DoesNotExist:
            return HttpResponse({"message": "ko", "status": 404})
        
        if 'video_duration' in request.POST:
            try:
                video_duration = int(request.POST.get('video_duration'))
                video_corso.durata_video = video_duration
                video_corso.save()
            except:
                print(f"Non è stato possibile parsare la durata del video: {video_duration}")
        
        if 'watched_seconds' in request.POST:
            try:
                watched_seconds = int(request.POST.get('watched_seconds'))
                if watched_seconds > stato_video.totale_secondi_visualizzati: #evito di tornare indietro
                    stato_video.totale_secondi_visualizzati = watched_seconds
                    stato_video.save()
            except:
                print(f"Non è stato possibile parsare i secondi visualizzati: {watched_seconds}")
                
        if 'is_started' in request.POST and request.POST.get('is_started').lower() == 'true':
            stato_video.iniziato = True
            stato_video.data_prima_visual = datetime.datetime.now()
        
        if 'update_visual_date' in request.POST and request.POST.get('update_visual_date').lower() == 'true':
            stato_video.data_ultima_visual = datetime.datetime.now()
        
        if 'is_completed' in request.POST and request.POST.get('is_completed').lower() == 'true':
            stato_video.completato = True
            stato_video.data_completamento = datetime.datetime.now()
        
        stato_video.save()
            
        return HttpResponse({"message": "ok", "status": 200})
    
class ConfiguraModuliView(View):
    template_name = 'home/configura-moduli.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'miei_corsi'}
        
        if request.user.is_superuser:
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            videocorsi_corso = corso.video_corsi.all()
            context['videocorsi_corso'] = videocorsi_corso
            context['corso'] = corso

            return render(request, self.template_name, context)
        else:
            return render(request, 'home/page-404.html')
    
    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        pass
    
    
class SalvaModuloView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            from django.core.exceptions import ValidationError
            context = { 'segment' : 'miei_corsi'}
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            videocorsi_corso = corso.video_corsi.all()        
            aziende = corso.aziende.all()

            titolo = request.POST.get('titolo')
            descrizione = request.POST.get('descrizione')
            ordine = request.POST.get('ordine')
            video_file = request.FILES.get('video_file')
            poster_file = request.FILES.get('poster_file')
            external_url = request.POST.get('external_url')

            try:
                videocorso = VideoCorso.objects.create(
                    titolo=titolo,
                    descrizione=descrizione,
                    ordine=ordine,
                    video_file=video_file,
                    poster_file=poster_file,
                    external_url=external_url,
                )
                videocorso.aziende.set(aziende)
                videocorso.save()
                corso.video_corsi.add(videocorso)
                corso.save()

                messages.success(request, 'VideoCorso aggiunto con successo.')
            except ValidationError as e:
                messages.error(request, 'Errore nell\'aggiunta del VideoCorso: ' + str(e))
            return redirect('configura_moduli', id_corso=corso.id)
        else:
            return render(request, 'home/page-404.html')

class OrdinaVideocorsiView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            context = { 'segment' : 'miei_corsi'}
            corso = Corso.objects.get(pk=kwargs.get('id_corso'))
            videocorsi_corso = corso.video_corsi.all()        
            try:
                new_order = json.loads(request.POST.get('order'))
                for item in new_order:
                    videocorso = VideoCorso.objects.get(pk=item['id'])
                    videocorso.ordine = item['order']
                    videocorso.save()
            except Exception as e:
                print(e)
                pass

            context['videocorsi_corso'] = videocorsi_corso
            context['corso'] = corso

            return redirect('configura_moduli', id_corso=corso.id)
        else:
            return render(request, 'home/page-404.html')

def scarica_attestato(request, id_corso):
    try:
        attestato = AttestatiVideo.objects.filter(utente=request.user, corso__id=id_corso).order_by('-data_conseguimento')[0]
    except IndexError:
        raise Http404("Attestato non trovato.")
    try:
        print(attestato.pdf.path)
        return FileResponse(open(attestato.pdf.path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404("File non trovato.")
    
class AttestatiView(View):
    template_name = 'home/utente_attestati.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        user = request.user
        video_corsi = VideoCorso.objects.all()
        azienda = user.customuser.azienda
        corsi = azienda.corsi.all()
        ultimi_attestati = {}

        for corso in corsi:
            ultimo_attestato = AttestatiVideo.objects.filter(utente=user, corso=corso).order_by('-data_conseguimento').first()
            if ultimo_attestato:
                ultimi_attestati[corso] = ultimo_attestato

        context = { 'segment' : 'utente_attestati', 'ultimi_attestati': ultimi_attestati}
        return render(request, self.template_name, context)
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'utente_attestati'}
        #TODO
        return render(request, self.template_name, context)

class SupportoView(View):
    template_name = 'home/supporto.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'supporto'}
        #TODO
        return render(request, self.template_name, context)

class AmministrazioneView(View):
    template_name = 'home/admin-dashboard.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            user = request.user
            aziende = Azienda.objects.all()
            corsi = Corso.objects.all()
            context = {
                'utente': user,
                'aziende': aziende,
                'corsi': corsi,
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))

class AggiungiCorsoView(View):
    template_name = 'home/aggiungi-corso.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            aziende = Azienda.objects.all()
            context = {
                'aziende': aziende,
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
        
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            titolo = request.POST.get('titolo')
            video_file = request.FILES.get('video_file')
            
            aziende_ids = [int(id) for id in request.POST.getlist('aziende')]
            aziende = Azienda.objects.filter(id__in=aziende_ids)
            # video_corso = VideoCorso.objects.create(titolo=titolo, video_file=video_file)
            corso = Corso.objects.create(titolo=titolo)
            corso.aziende.set(aziende)
            corso.save()
            return HttpResponseRedirect(reverse('amministrazione'))
        else:
            return HttpResponseRedirect(reverse('home'))

class AggiungiUtenteView(View):
    template_name = 'home/aggiungi-utente.html'
    
    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = {
            'aziende': Azienda.objects.all(),
            'segment': 'amministrazione-utenti-aggiungi',
            'breadcrumb_level_1': 'Amministrazione', 
            'breadcrumb_level_2': 'Utenti', 
            'breadcrumb_level_3': 'Aggiungi utente'
            
        }
        return render(request, self.template_name, context)

    
    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        context = {
            'aziende': Azienda.objects.all(),
            'segment': 'amministrazione-utenti-aggiungi',
            'breadcrumb_level_1': 'Amministrazione', 
            'breadcrumb_level_2': 'Utenti', 
            'breadcrumb_level_3': 'Aggiungi utente'
        }
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        nome = request.POST.get('nome')
        cognome = request.POST.get('cognome')
        azienda_id = request.POST.get('azienda')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        is_staff = request.POST.get('is_staff', False)
        is_staff = True if is_staff == 'on' else False
        is_valid = True

        if User.objects.filter(username=username).exists():
            context['message'] = "Username già esistente!"
            context['message_class'] =  'alert-danger'
            is_valid = False
            
        if User.objects.filter(email=email).exists():
            context['message'] = "L'email utilizzata risulta già associata ad un altro utente"
            context['message_class'] =  'alert-danger'
            is_valid = False
            
        if is_valid:
            
            user = User.objects.create_user(username=username, password=password, first_name=nome, last_name=cognome, email=email, is_staff=is_staff, is_superuser=False)
            azienda = Azienda.objects.get(id=azienda_id)
            utente = CustomUser.objects.create(user=user, azienda=azienda, phone_number=phone_number)
            context['message'] =  'Utente aggiunto con successo!'
            context['message_class'] =  'alert-success'  
            utente.save()    

            mail = Mail(
                to_who=email,
                subject="Benvenuto!",
                html_text="Benvenuto, {}! Il tuo account è stato creato con successo.".format(nome),
                request_date = datetime.datetime.now(),
            )
            mail.save()
        
        return render(request, self.template_name, context)
    
class CreaQuizView(View):
    template_name = 'home/crea_quiz.html'

    # Questa funzione è per garantire che solo gli utenti staff possano accedere a questa vista
    def test_func(self):
        return self.request.user.is_staff
    
    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        # Assumi che 'id' sia l'ID del VideoCorso. Ottienilo dai kwargs o in qualche altro modo.
        corso = Corso.objects.get(pk=kwargs.get('id_corso'))
        # i videocorsi associati al corso
        videocorsi = corso.video_corsi.all()
        return render(request, self.template_name, {'videocorso': videocorsi, 'corso': corso})

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        corso = Corso.objects.get(pk=kwargs.get('id_corso'))
        videocorsi = corso.video_corsi.all()
        titolo_quiz = request.POST.get('titolo_quiz')

        quiz = Quiz.objects.create(corso=corso, titolo=titolo_quiz)

        # Itera attraverso le domande inviate
        for key in request.POST:
            if key.startswith('domanda_'):
                num_domanda = key.split('_')[1]
                testo_domanda = request.POST[key]

                domanda = Domanda.objects.create(quiz=quiz, testo=testo_domanda)

                # Itera attraverso le opzioni per questa specifica domanda
                for i in range(1, 5):
                    testo_opzione = request.POST.get(f'opzione_{num_domanda}_{i}')
                    corretta = request.POST.get(f'risposta_corretta_{num_domanda}') == f'opzione_{i}'
                    OpzioneRisposta.objects.create(domanda=domanda, testo_opzione=testo_opzione, corretta=corretta)

        return redirect('utente_corso_dettaglio', id_corso=corso.id)
    
# vista per eseguire il quiz
class QuizView(View):
    template_name = 'home/quiz.html'

    def get(self, request, *args, **kwargs):
        # videocorso = VideoCorso.objects.get(pk=kwargs.get('id_corso'))
        corso = Corso.objects.get(pk=kwargs.get('id_corso'))
        alert = None
        # seleziono il quiz relativo al corso, l'ultimo creato
        quiz = Quiz.objects.filter(corso=corso).last()
        if quiz is None:
            alert = "Non è stato ancora creato un quiz per questo corso."
        return render(request, self.template_name, {'quiz': quiz, 'corso': corso, 'alert': alert})

    def post(self, request, *args, **kwargs):
        # videocorso = VideoCorso.objects.get(pk=kwargs.get('id_corso'))
        corso = Corso.objects.get(pk=kwargs.get('id_corso'))
        quiz = Quiz.objects.filter(corso=corso).last()

        risultati = {}
        risposte_corrette = 0 

        for key in request.POST:
            if key.startswith('risposta_'):
                num_domanda = key.split('_')[1]
                domanda = Domanda.objects.get(pk=num_domanda)
                opzione_selezionata = int(request.POST[key])  # Converti in intero
                opzione_selezionata_obj = OpzioneRisposta.objects.get(id=opzione_selezionata)
                testo_risposta = opzione_selezionata_obj.testo_opzione
                opzione_corretta = OpzioneRisposta.objects.get(domanda=domanda, corretta=True).id
                # Memorizzo il risultato e la risposta data nel dizionario
                risultato = opzione_selezionata == opzione_corretta
                risultati[num_domanda] = {'risultato': risultato, 'risposta_data': opzione_selezionata, 'testo_risposta': testo_risposta}
                # Se la risposta è corretta, incremento il contatore
                if risultato:
                    risposte_corrette += 1

        risultati['risposte_corrette'] = risposte_corrette
        risultati['test_superato'] = risposte_corrette == quiz.domande.count()
        quiz_attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, risultati=risultati)

        if risultati['test_superato']:
            # Se l'utente ha superato il test, genero l'attestato
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            p.setFont("Helvetica", 24)
            p.drawString(100, 700, "Attestato di superamento del corso")
            p.setFont("Helvetica", 16)
            p.drawString(100, 650, f"Conseguito da: {request.user.username}")
            p.drawString(100, 600, f"Corso: {quiz_attempt.quiz.corso.titolo}")
            p.drawString(100, 550, f"Data: {quiz_attempt.timestamp.strftime('%d/%m/%Y')}")

            p.showPage()
            p.save()

            # Salvo il PDF in un file temporaneo che si trova nella cartella media/attestati
            import shutil

            directory = f"media/attestati/{request.user.username}_{request.user.customuser.id}"
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Crea il file nel percorso originale
            filename_originale = f"{quiz_attempt.quiz.corso.titolo}.pdf"
            with open(filename_originale, 'wb') as f:
                f.write(buffer.getvalue())

            # Sposto il file nella cartella media/attestati
            filename_destinazione = os.path.join(directory, filename_originale)
            if os.path.exists(filename_destinazione):
                os.remove(filename_destinazione)
            shutil.move(filename_originale, filename_destinazione)

            # Creo un nuovo AttestatiVideo con il percorso al file PDF
            AttestatiVideo.objects.create(
                utente=request.user,
                corso=quiz_attempt.quiz.corso,
                data_conseguimento=quiz_attempt.timestamp,
                pdf=filename_destinazione
            )        


        return redirect('risultati_quiz', id_corso=corso.id, id_quiz_attempt=quiz_attempt.id)
    
class QuizRisultatiView(View):
    template_name = 'home/risultati-quiz.html'

    def get(self, request, *args, **kwargs):
        quiz_attempt = QuizAttempt.objects.get(pk=kwargs.get('id_quiz_attempt'))
        numero_domande = quiz_attempt.quiz.domande.count()
        risultati = [
                {
                    'domanda': domanda, 
                    'corretta': quiz_attempt.risultati.get(str(domanda.id)), 
                    'risposta_data': quiz_attempt.risultati[str(domanda.id)]['risposta_data'],
                    'testo_risposta': quiz_attempt.risultati[str(domanda.id)]['testo_risposta']
            } 
                for domanda in quiz_attempt.quiz.domande.all()
            ]

        return render(request, self.template_name, {'quiz_attempt': quiz_attempt, 'risultati': risultati, 'numero_domande': numero_domande})