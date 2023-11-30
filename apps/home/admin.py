from django.contrib import admin
from .models import *


class StatoVideoAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'iniziato', 'completato')

admin.site.register(Azienda)
admin.site.register(CustomUser)
admin.site.register(VideoCorso)
admin.site.register(StatoVideo, StatoVideoAdmin)
admin.site.register(AttestatiVideo)
admin.site.register(Quiz)
admin.site.register(Domanda)
admin.site.register(OpzioneRisposta)
