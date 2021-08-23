import base64
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template import loader
from .models import SchedTime

import matplotlib.pyplot as plt
import psutil
import cpuinfo
import os
import time
import sched
import io
import socket
import io
import urllib
import platform
import subprocess

scheduler = sched.scheduler(time.time, time.sleep)


def formatar(valor):
    return round(valor/(1024*1024*1024), 2)


def pegarInformacoesRedes():
    processos = psutil.pids()
    lista = []

    for i in processos:
        processo = psutil.Process(i)
        informacaoRedes = processo.connections()
        if (len(informacaoRedes) > 0):
            if(len(informacaoRedes[0].raddr) > 0):
                enderecoRemoto = informacaoRedes[0].raddr[0]
                portaRemota = informacaoRedes[0].raddr[1]
            informacoesProcessos = {
                'pid': i,
                'tipoEndereco': obtem_nome_familia(informacaoRedes[0].family),
                'tipo': obtem_tipo_socket(informacaoRedes[0].type),
                'status': informacaoRedes[0].status,
                'endereco': informacaoRedes[0].laddr[0],
                'portaLocal': informacaoRedes[0].laddr[1],
                'enderecoRemoto': enderecoRemoto,
                'portaRemota': portaRemota
            }
            lista.append(informacoesProcessos)
        else:
            lista.append({'pid': i})
    return lista


def retorna_codigo_ping(hostname):
    """Usa o utilitario ping do sistema operacional para encontrar   o host. ('-c 5') indica, em sistemas linux, que deve mandar 5   pacotes. ('-W 3') indica, em sistemas linux, que deve esperar 3   milisegundos por uma resposta. Esta funcao retorna o codigo de   resposta do ping """

    plataforma = platform.system()
    args = []
    if plataforma == "Windows":
        args = ["ping", "-n", "1", "-l", "1", "-w", "100", hostname]

    else:
        args = ['ping', '-c', '1', '-W', '1', hostname]

    ret_cod = subprocess.call(args,
                              stdout=open(os.devnull, 'w'),
                              stderr=open(os.devnull, 'w'))
    return ret_cod


def verifica_hosts(base_ip):
    """Verifica todos os host com a base_ip entre 1 e 255 retorna uma lista com todos os host que tiveram resposta 0 (ativo)"""
    print("Mapeando\r")
    host_validos = []
    return_codes = dict()
    for i in range(1, 255):

        return_codes[base_ip +
                     '{0}'.format(i)] = retorna_codigo_ping(base_ip + '{0}'.format(i))
        if i % 20 == 0:
            print(".", end="")
        if return_codes[base_ip + '{0}'.format(i)] == 0:
            host_validos.append(base_ip + '{0}'.format(i))
    print("\nMapping ready...")

    return host_validos


def hosts_validos(ip_string):
    ip_lista = ip_string.split('.')
    base_ip = ".".join(ip_lista[0:3]) + '.'
    return verifica_hosts(base_ip)


def obtem_nome_familia(familia):
    if familia == socket.AF_INET:
        return("IPv4")
    elif familia == socket.AF_INET6:
        return("IPv6")
    elif familia == socket.AF_UNIX:
        return("Unix")
    else:
        return("-")


def obtem_tipo_socket(tipo):
    if tipo == socket.SOCK_STREAM:
        return("TCP")
    elif tipo == socket.SOCK_DGRAM:
        return("UDP")
    elif tipo == socket.SOCK_RAW:
        return("IP")
    else:
        return("-")


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
    cpu_percent = []
    for corePercent in psutil.cpu_percent(percpu=True):
        cores.append(corePercent)

    for i in range(30):
        cpu_percent_info = psutil.cpu_percent()
        cpu_percent.append(cpu_percent_info)
        time.sleep(0.1)

    plt.figure(figsize=(10, 10))

    ax = plt.subplot(1, 1, 1)
    ax.plot(range(30), cpu_percent)

    ax.set(xlabel='tempo(s)', ylabel='cpu_percent',
           title='Gráfico de variação do uso de cpu')

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

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
        'graficoUrl': uri
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

    informacoes = pegarInformacoesRedes()

    ip_string = request.POST.get('ip')
    hosts = ""
    if(ip_string is not None):
        hosts = hosts_validos(ip_string)
    else:
        hosts = ""

    template = loader.get_template('rede.html')
    context = {
        'interface_net': rede['Ethernet 2'][0].address,
        'internet_vel': psutil.net_if_stats()['Ethernet 2'][2],
        'mascara': rede['Ethernet 2'][0].netmask,
        'informacoesProcessos': informacoes,
        'hosts_validos': hosts
    }
    return HttpResponse(template.render(context, request))


def arquivos(request):
    dicArquivos = {}
    caminho = request.POST.get('dir')
    caminhoRapido = request.POST.get('dirButton')
    listarArquivos(caminho, caminhoRapido, dicArquivos)
    eventoIniciado = time.ctime()
    scheduler.enter(0, 1, listarArquivos, ('', '', {}))
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


def logArquivos(request):
    listaInformacoes = []
    for s in SchedTime.objects.values_list('id', 'start_time', 'stop_time'):
        dict = {
            'id': s[0],
            'start_time': s[1],
            'stop_time': s[2]
        }
        listaInformacoes.append(dict)
    template = loader.get_template('log_arquivos.html')
    context = {
        'scheds': listaInformacoes
    }
    return HttpResponse(template.render(context, request))
