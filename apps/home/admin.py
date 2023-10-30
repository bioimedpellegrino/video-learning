from django.contrib import admin
from .models import *


class StatoVideoAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'iniziato', 'completato')

admin.site.register(Azienda)
admin.site.register(CustomUser)
admin.site.register(VideoCorso)
admin.site.register(StatoVideo, StatoVideoAdmin)