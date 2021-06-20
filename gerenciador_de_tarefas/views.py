from django.http import HttpResponse
from django.template import loader
import psutil
import cpuinfo
import os
import time
import subprocess

def formatar(valor):
    return round(valor/(1024*1024*1024), 2)

def index(request):
    disco = psutil.disk_usage('.')
    template = loader.get_template('index.html')    
    context = {
        'disco_total': formatar(disco.total),
        'disco_em_uso': formatar(disco.used),
        'disco_livre': formatar(disco.free),
        'disco_percentual_usado': disco.percent,
    }
    return HttpResponse(template.render(context, request))

def processador(request):
    cores = []
    for corePercent in psutil.cpu_percent(percpu=True):
        cores.append(corePercent)

    template = loader.get_template('processador.html')
    context = {
        'cpu_name': cpuinfo.get_cpu_info()['brand_raw'],
        'archtecture': cpuinfo.get_cpu_info()['arch'],
        'bits': cpuinfo.get_cpu_info()['bits'],
        'nucleos_logic_tot': psutil.cpu_count(logical = True),
        'freq_total': psutil.cpu_freq().max,
        'freq_uso': psutil.cpu_freq().current,
        'nucleos_fisic_tot': psutil.cpu_count(logical = False),
        'cpu_percent': cores,
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

def arquivos(request):
    lista = os.listdir()
    dic = {}
    for i in lista:
        if os.path.isfile(i):
            dic[i] = []
            dic[i].append(os.stat(i).st_size)
            dic[i].append(os.stat(i).st_atime)
            dic[i].append(os.stat(i).st_mtime)
    template = loader.get_template('arquivos.html')
    context = {
        'arquivos': dic,
    }
    return HttpResponse(template.render(context, request))

def sub_processos(request):
    def mostra_info(pid):
        try:
            p = psutil.Process(pid)
            texto = '{:6}'.format(pid)
            texto = texto + '{:11}'.format(p.num_threads())
            texto = texto + " " + time.ctime(p.create_time()) + " "
            texto = texto + '{:8.2f}'.format(p.cpu_times().user)
            texto = texto + '{:8.2f}'.format(p.cpu_times().system)
            texto = texto + '{:10.2f}'.format(p.memory_percent()) + " MB"
            rss = p.memory_info().rss/1024/1024
            texto = texto + '{:10.2f}'.format(rss) + " MB"
            vms = p.memory_info().vms/1024/1024
            texto = texto + '{:10.2f}'.format(vms) + " MB"
            texto = texto + " " + p.exe()
            return texto
        except:
            pass  

    lista = psutil.pids()
    novaLista = []

    for i in lista:
        novaLista.append(mostra_info(i))

    template = loader.get_template('sub_processos.html')
    context = {
        'processos': novaLista,
    }
    return HttpResponse(template.render(context, request))