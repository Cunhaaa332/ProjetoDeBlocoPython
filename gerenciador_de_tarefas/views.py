from django.http import HttpResponse
from django.template import loader
import psutil

def formatar_memoria(valor):
    return round(valor/(1024*1024*1024), 2)

def index(request):
    disco = psutil.disk_usage('.')
    template = loader.get_template('index.html')
    context = {
        'nome': "Gerenciador de tarefas",
        'disco_total': formatar_memoria(disco.total),
        'disco_em_uso': formatar_memoria(disco.used),
        'disco_livre': formatar_memoria(disco.free),
        'disco_percentual_usado': disco.percent,
    }
    return HttpResponse(template.render(context, request))
