from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('processador/', views.processador, name='processador'),
    path('memoria/', views.memoria, name='memoria'),
    path('rede/', views.rede, name='rede'),
    path('arquivos/', views.arquivos, name='arquivos'),
    path('arquivos/logArquivos/', views.logArquivos, name='log_arquivos'),
    path('sub_processos/', views.sub_processos, name='sub_processos'),
]