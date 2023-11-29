from django import template
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from custom_mail.models import Mail
from django.shortcuts import redirect, render
from django.views.generic import View
from django.db import IntegrityError
from .forms import *

import datetime

@login_required(login_url="/login/")
def index(request):
    
    context = {'segment': 'index','breadcrumb_level_1': 'Home'}
    if request.user.is_staff or request.user.is_superuser:
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
        context = { 'segment' : 'amministrazione-aziende'}
        if request.user.is_superuser:
            aziende = Azienda.objects.all()
            context["aziende"] = aziende
            return render(request, self.template_name, context)
        profile = CustomUser.objects.get(user=request.user)
        aziende = profile.aziende.all()
        utenti = CustomUser.objects.filter(azienda__isnull=True)
        self.context["aziende"] = aziende
        self.context["utenti"] = utenti
        
        return render(request, self.template_name, context)

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

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-videocorsi'}
        #TODO
        video_corsi = VideoCorso.objects.all()
        context["video_corsi"] = video_corsi
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
        #TODO
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
        context = { 'segment' : 'utente_corsi'}
        #TODO
        user = request.user
        # Se l'utente deve avere corsi specifici e non tutti quelli dell'azienda uso var video_corsi_spec
        video_corsi = VideoCorso.objects.filter(aziende=user.customuser.azienda)
        context["video_corsi"] = video_corsi

        return render(request, self.template_name, context)
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'utente_corsi'}
        #TODO
        return render(request, self.template_name, context)

# Dettagli corso deve essere accessibile solo dall'admin e deve avere i dati relativi al corso
class DettagliCorsoView(View):
    template_name = 'home/utente_corso_dettagli.html'

    def get(self, request, *args, **kwargs):
        #TODO
        videocorso = VideoCorso.objects.get(pk=kwargs.get('id_corso'))
        utenti = CustomUser.objects.all()
        aziende_all = Azienda.objects.all()
        aziende_video_corso = videocorso.aziende.all()
        context = {
            'segment' : 'utente_corso_dettaglio',
            'aziende_all': aziende_all,
            'aziende_video_corso': aziende_video_corso,
            'videocorso': videocorso,
        }
        return render(request, self.template_name, context)
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        videocorso = VideoCorso.objects.get(pk=kwargs.get('id_corso'))
        utenti = CustomUser.objects.all()
        aziende_all = Azienda.objects.all()
        id_azienda_aggiunta = request.POST.get('azienda')
        if id_azienda_aggiunta:
            azienda_aggiunta = Azienda.objects.get(pk=id_azienda_aggiunta)
            videocorso.aziende.add(azienda_aggiunta)
            videocorso.save()
        aziende_video_corso = videocorso.aziende.all()


        context = {
            'segment' : 'utente_corso_dettaglio',
            'aziende_all': aziende_all,
            'aziende_video_corso': aziende_video_corso,
            'videocorso': videocorso,
        }
        return render(request, self.template_name, context)

class WatchVideoCorsoView(View):
    template_name = 'home/watch-video.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'miei_corsi'}
        id_video = kwargs.get('id_video')
        custom_user = CustomUser.objects.get(user=request.user)
        try:
            video_corso = VideoCorso.objects.get(pk=id_video)
            context['breadcrumb_level_1'] = video_corso.titolo
        except VideoCorso.DoesNotExist:
            return render(request, 'home/page-404.html')
        
        if not custom_user.azienda in video_corso.aziende.all():
            return render(request, 'home/page-403.html')
        else:
            stato_video, _ = StatoVideo.objects.get_or_create(utente=custom_user, video_corso=video_corso)
            context["video_corso"] = video_corso
            context["custom_user"] = custom_user
            context["stato_video"] = stato_video
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

class AttestatiView(View):
    template_name = 'home/utente_attestati.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'utente_attestati'}
        #TODO
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
            aziende = Azienda.objects.all()
            video_corsi = VideoCorso.objects.all()
            context = {
                'aziende': aziende,
                'video_corsi': video_corsi,
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
            video_corso = VideoCorso.objects.create(titolo=titolo, video_file=video_file)
            video_corso.aziende.set(aziende)
            video_corso.save()
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
            )
            mail.save()
        
        return render(request, self.template_name, context)
