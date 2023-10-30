from django import template
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from django.shortcuts import redirect, render
from django.views.generic import View
from django.db import IntegrityError
from .forms import *

import datetime

@login_required(login_url="/login/")
def index(request):
    
    context = {'segment': 'index','breadcrumb_level_1': 'Home'}
    if request.user.is_staff or request.user.is_superuser:
        html_template = loader.get_template('home/admin-dashboard.html')
    else:
        html_template = loader.get_template('home/utente_corsi.html')
    return HttpResponse(html_template.render(context, request))


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
        #TODO
        return render(request, self.template_name, context)


class VideoCorsiView(View):
    template_name = 'home/video-corsi.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-videocorsi'}
        #TODO
        return render(request, self.template_name, context)

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-videocorsi'}
        #TODO
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
        return render(request, self.template_name, context)
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'utente_corsi'}
        #TODO
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

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = VideoCorsoForm()
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
        
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = VideoCorsoForm(request.POST, request.FILES)
            if form.is_valid():
                video_corso = form.save()
                return HttpResponseRedirect(reverse('amministrazione'))
            else:
                context = {
                    'form': form,
                }
                return render(request, self.template_name, context)
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
        phone_number = request.POST.get('phone_number')
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
        
        return render(request, self.template_name, context)
