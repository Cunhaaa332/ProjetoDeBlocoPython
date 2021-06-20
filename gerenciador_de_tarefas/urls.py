from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('processo/', views.processador, name='processador'),
    path('memoria/', views.memoria, name='memoria'),
    path('rede/', views.rede, name='rede'),
    path('arquivos/', views.arquivos, name='arquivos'),
    path('sub_processos/', views.sub_processos, name='sub_processos'),
]