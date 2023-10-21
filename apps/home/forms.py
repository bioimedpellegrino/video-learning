from django import forms
from .models import *

class VideoCorsoForm(forms.ModelForm):
    class Meta:
        model = VideoCorso
        fields = ['titolo', 'aziende', 'video_file']
        widgets = {
            'aziende': forms.CheckboxSelectMultiple()
        }
    
    def __init__(self, *args, **kwargs):
        super(VideoCorsoForm, self).__init__(*args, **kwargs)
        self.fields['aziende'].required = False
        self.fields['aziende'].help_text = "Seleziona le aziende che potranno visualizzare il video corso. Se non selezioni nessuna azienda, il video corso sarà visibile a tutte le aziende."
        self.fields['aziende'].label = "Aziende"
        self.fields['video_file'].help_text = "Seleziona il file video da caricare. Estensioni consentite: mp4, webm, ogg."
        self.fields['video_file'].label = "File Video"
    
    def clean(self):
        cleaned_data = super(VideoCorsoForm, self).clean()
        aziende = cleaned_data.get("aziende")
        if aziende is None:
            cleaned_data['aziende'] = Azienda.objects.all()
        return cleaned_data
    
    def save(self, commit=True):
        video_corso = super(VideoCorsoForm, self).save(commit=False)
        video_corso.save()
        return video_corso



    
