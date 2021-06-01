from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('processo/', views.processo, name='processo'),
]