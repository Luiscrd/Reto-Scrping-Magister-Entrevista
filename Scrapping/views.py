from django.shortcuts import render
from .models import Centros

def index(request):

    lista_escuelas = Centros.objects.all()
    
    return render(request, 'index.html', {
        "escuelas":lista_escuelas,
    })