from django.views.generic import TemplateView
from django.shortcuts import render
from .forms import MessageForm
from .models import Converter


class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request):
        form = MessageForm()
        return render(request, self.template_name, {'form': form, 'translated': ""})
    
    def post(self, request):
        form = MessageForm(data=request.POST)

        if form.is_valid():
            text = form.cleaned_data['post']
            conv = Converter()
            for line in text.split('\n'):
                conv.parse_line(line)
            translated = "".join(conv.output)
            args = {'form': form, 'translated': translated}
        else:
            args = {'form': form, 'translated': ""}
        
        
        return render(request, self.template_name, args)





