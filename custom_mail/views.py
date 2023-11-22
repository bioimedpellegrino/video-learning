from __future__ import print_function
from __future__ import absolute_import
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from .models import Mail

class RenderMailView(View):

    template_name = ''
 
    def get(self, request, *args, **kwargs):
        m = Mail.objects.get(uuid=kwargs.get('uuid'))
        self.template_name = 'mail/' + m.template_name + '.html'
        return HttpResponse(m.html_text)
    
class SentMailListView(View):

    template_name = 'custom_mail/sent_mail_list.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser is True:
            from .models import Mail

            mails=Mail.objects.all()

            return render(request, self.template_name, {'mails': mails })

        else:
            # Unauthorized
            return render(request, 'errors/401.html', {'page_content': ''}, status=401)

class SentMailView(View):

    template_name = 'custom_mail/sent_mail_detail.html'

    def get(self, request, *args, **kwargs):
        mail_id = kwargs.get("id", None)

        if request.user.is_superuser is True:
            from .models import Mail

            if mail_id:
                mail=Mail.objects.get(pk=mail_id)
            else:
                mail=None

            return render(request, self.template_name, {'mail': mail })

        else:
            # Unauthorized
            return render(request, 'errors/401.html', {'page_content': ''}, status=401)