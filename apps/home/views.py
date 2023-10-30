from django import template
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from django.shortcuts import render
from django.views.generic import View
from django.db import IntegrityError
from .forms import *

@login_required(login_url="/login/")
def index(request):
    
    context = {'segment': 'index'}
    if request.user.is_staff or request.user.is_superuser:
        html_template = loader.get_template('home/admin-dashboard.html')
    else:
        html_template = loader.get_template('home/corsi.html')
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

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-aziende'}
        profile = CustomUser.objects.get(user=request.user)
        aziende = profile.aziende.all()
        context["aziende"] = aziende
        
        return render(request, self.template_name, context)

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-aziende'}
        #TODO
        return render(request, self.template_name, context)

class UtentiView(View):
    template_name = 'home/utenti.html'

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-utenti'}
        #TODO
        return render(request, self.template_name, context)

    @method_decorator(staff_member_required(login_url="page-403.html"), login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        context = { 'segment' : 'amministrazione-utenti'}
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
            aziende = request.POST.getlist('aziende')
            video_file = request.FILES.get('video_file')
            
            aziende = Azienda.objects.filter(id__in=aziende)
            video_corso = VideoCorso.objects.create(titolo=titolo, video_file=video_file)
            video_corso.aziende.set(aziende)
            video_corso.save()
            return HttpResponseRedirect(reverse('amministrazione'))
        else:
            return HttpResponseRedirect(reverse('home'))
        
class AggiungiAziendaView(View):
    template_name = 'home/aggiungi-azienda.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = AziendaForm()
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
        
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = AziendaForm(request.POST)
            if form.is_valid():
                azienda = form.save()
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

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            context = {
                'aziende': Azienda.objects.all(),
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
        
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            username = request.POST.get('username')
            password = request.POST.get('password')
            nome = request.POST.get('nome')
            cognome = request.POST.get('cognome')
            azienda_id = request.POST.get('azienda')
            email = request.POST.get('email')
            # is_staff = request.POST.get('is_staff')
            is_superuser = request.POST.get('is_superuser')

            try:
                # Creo l'oggetto User associato usando nome per first name e cognome per last name e se is_superuser è True lo rendo superuser
                user = User.objects.create_user(username=username, password=password, first_name=nome, last_name=cognome, email=email, is_superuser=is_superuser)
            except IntegrityError:
                message = "Username già esistente!"
                context = {
                    'aziende': Azienda.objects.all(),
                    'username': username,
                    'password': password,
                    'nome': nome,
                    'cognome': cognome,
                    'email': email,
                    'message': message,
                }
                return render(request, self.template_name, context)
            
            azienda = Azienda.objects.get(id=azienda_id)
            utente = CustomUser.objects.create(user=user, azienda=azienda)
            utente.save()            

            message = "Utente aggiunto con successo!"
            context = {
                'aziende': Azienda.objects.all(),
                'message': message,
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
