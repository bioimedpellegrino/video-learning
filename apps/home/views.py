from django import template
from django.contrib.auth.decorators import login_required
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

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

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
            form = UtenteForm()
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
        
    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = UtenteForm(request.POST)
            if form.is_valid():
                utente = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                email = form.cleaned_data.get('email')
                try:
                # Creo l'oggetto User associato
                    user = User.objects.create_user(username=username, email=email, password=password)
                except IntegrityError:
                    message = "Username già esistente!"
                    context = {
                        'form': form,
                        'message': message,
                    }
                    return render(request, self.template_name, context)

                utente.user = user
                utente.save()

                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    message = "Utente aggiunto con successo!"
                    context = {
                        'form': form,
                        'message': message,
                    }
                    return render(request, self.template_name, context)
                else:
                    message = "Errore durante la creazione dell'utente!"
                    context = {
                        'form': form,
                        'message': message,
                    }
                    return render(request, self.template_name, context)
            else:
                errors = form.errors
                message = "Errore durante la creazione dell'utente!"
                context = {
                    'form': form,
                    'message': message,
                    'errors': errors,
                }
                return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect(reverse('home'))
