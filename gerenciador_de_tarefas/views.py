from django.http import HttpResponse
from django.template import loader
import psutil
import cpuinfo
import os
import time

def formatar(valor):
    return round(valor/(1024*1024*1024), 2)




def index(request):
    lista = os.listdir()
    dic = {}
    for i in lista:
        if os.path.isfile(i):
            dic[i] = []
            dic[i].append(os.stat(i).st_size)
            dic[i].append(os.stat(i).st_atime)
            dic[i].append(os.stat(i).st_mtime)

    
    
    disco = psutil.disk_usage('.')
    template = loader.get_template('index.html')    
    context = {
        'disco_total': formatar(disco.total),
        'disco_em_uso': formatar(disco.used),
        'disco_livre': formatar(disco.free),
        'disco_percentual_usado': disco.percent,
        'arquivos': dic,
    }
    return HttpResponse(template.render(context, request))

def processo(request):
    template = loader.get_template('processo.html')
    context = {
        'cpu_name': cpuinfo.get_cpu_info()['brand_raw'],
        'archtecture': cpuinfo.get_cpu_info()['arch'],
        'bits': cpuinfo.get_cpu_info()['bits'],
        'nucleos_logic_tot': psutil.cpu_count(logical = True),
        'freq_total': psutil.cpu_freq().max,
        'freq_uso': psutil.cpu_freq().current,
        'nucleos_fisic_tot': psutil.cpu_count(logical = False),
        'cpu_percent': psutil.cpu_percent(),
    }
    return HttpResponse(template.render(context, request))

def memoria(request):
    memoria = psutil.swap_memory()
    template = loader.get_template('memoria.html')
    context = {
        'tot_memory': formatar(memoria[0]),
        'memory_used': formatar(memoria[1]),
        'memory_free': formatar(memoria[2]),
        'percent_memory_used': memoria[3],
    }
    return HttpResponse(template.render(context, request))

def rede(request):
    rede = psutil.net_if_addrs()
    template = loader.get_template('rede.html')
    context = {
        'interface_net': rede['Ethernet 2'][0].address,
        'internet_vel': psutil.net_if_stats()['Ethernet 2'][2],
    }
    return HttpResponse(template.render(context, request))

