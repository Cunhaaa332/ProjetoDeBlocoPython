from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template import loader
from .models import SchedTime
import psutil
import cpuinfo
import os
import time
import sched

scheduler = sched.scheduler(time.time, time.sleep)

def formatar(valor):
    return round(valor/(1024*1024*1024), 2)

def listarArquivos(caminho, caminhoRapido, dicArquivos):
    if (caminho != None or caminhoRapido != None):
        if(caminhoRapido != None):
            path = os.path.expanduser("~\\" + caminhoRapido)
        else:
            path = caminho
        os.chdir(path)
        listaArquivos = os.listdir(path)
        for i in listaArquivos:
            dicArquivos[i] = []
            dicArquivos[i].append(os.stat(i).st_size)
            dicArquivos[i].append(time.ctime(os.stat(i).st_atime))
            dicArquivos[i].append(time.ctime(os.stat(i).st_mtime))
            if(os.path.isfile(i)):
                dicArquivos[i].append("Arquivo")
            else:
                dicArquivos[i].append("Pasta")

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
        'nucleos_logic_tot': psutil.cpu_count(logical=True),
        'freq_total': psutil.cpu_freq().max,
        'freq_uso': psutil.cpu_freq().current,
        'nucleos_fisic_tot': psutil.cpu_count(logical=False),
        'cores': cores,
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
    dicArquivos = {}
    caminho = request.POST.get('dir')
    caminhoRapido = request.POST.get('dirButton')
    listarArquivos(caminho, caminhoRapido, dicArquivos)
    eventoIniciado = time.ctime()
    scheduler.enter(0, 1, listarArquivos, ('','', {}))
    scheduler.run()
    eventoTerminado = time.ctime()
    template = loader.get_template('arquivos.html')
    context = {
        'arquivos': dicArquivos,
    }
    schedTime = SchedTime(start_time=eventoIniciado, stop_time=eventoTerminado)
    schedTime.save()
    return HttpResponse(template.render(context, request))

def sub_processos(request):
    def mostra_info(pid):
        try:
            p = psutil.Process(pid)
            rss = p.memory_info().rss/1024/1024
            vms = p.memory_info().vms/1024/1024
            memory_percent = p.memory_percent()
            cpu_times_user = p.cpu_times().user
            cpu_times_system = p.cpu_times().system
            dict_info = {
                'pid': pid,
                'num_threads': p.num_threads(),
                'create_time':  time.ctime(p.create_time()),
                'cpu_times_user': '{:8.2f}'.format(cpu_times_user),
                'cpu_times_system': '{:8.2f}'.format(cpu_times_system),
                'memory_percent': '{:10.2f}'.format(memory_percent) + " MB",
                'rss': '{:10.2f}'.format(rss) + " MB",
                'vms': '{:10.2f}'.format(vms) + " MB",
                'exe': p.exe()
            }
            return dict_info
        except:
            pass

    listaProcessos = psutil.pids()
    novaListaProcessos = []

    for i in listaProcessos:
        novaListaProcessos.append(mostra_info(i))
    
    subProcessosPaginator = Paginator(novaListaProcessos, 10)
    page_num = request.GET.get('page')
    page = subProcessosPaginator.get_page(page_num)
    template = loader.get_template('sub_processos.html')
    context = {
        'page': page,
    }
    return HttpResponse(template.render(context, request))
