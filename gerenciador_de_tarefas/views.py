from django.http import HttpResponse
from django.template import loader
import psutil
import cpuinfo

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

def processo(request):
    template = loader.get_template('processo.html')
    context = {
        'nome': "Gerenciador de tarefas",
        'cpu_name': cpuinfo.get_cpu_info()['brand_raw'],
        'archtecture': cpuinfo.get_cpu_info()['arch'],
        'bits': cpuinfo.get_cpu_info()['bits'],
        'nucleos_logic_tot': psutil.cpu_count(logical = True),
        'nucleos_fisic_tot': psutil.cpu_count(logical = False),
        'cpu_percent': psutil.cpu_percent(),
    }
    return HttpResponse(template.render(context, request))

def memoria(request):
    memoria = psutil.swap_memory()
    template = loader.get_template('memoria.html')
    context = {
        'nome': "Gerenciador de tarefas",
        'tot_memory': formatar_memoria(memoria[0]),
        'memory_used': formatar_memoria(memoria[1]),
        'memory_free': formatar_memoria(memoria[2]),
        'percent_memory_used': memoria[3],
    }
    return HttpResponse(template.render(context, request))

