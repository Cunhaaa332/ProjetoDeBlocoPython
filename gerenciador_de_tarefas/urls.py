from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('processador/', views.processador, name='processador'),
    path('memoria/', views.memoria, name='memoria'),
    path('rede/', views.rede, name='rede'),
    path('arquivos/', views.arquivos, name='arquivos'),
    path('logArquivos/', views.logArquivos, name='logArquivos'),
    path('sub_processos/', views.sub_processos, name='sub_processos'),
]