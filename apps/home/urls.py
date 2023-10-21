# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import *

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path("amministrazione/", AmministrazioneView.as_view(), name="amministrazione"),
    path("aggiungi_corso/", AggiungiCorsoView.as_view(), name="aggiungi_corso"),



    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
