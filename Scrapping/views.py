from django.shortcuts import render
from django.shortcuts import redirect
from itertools import count
import requests
from bs4 import BeautifulSoup
from .models import Centros

def index(request):

    lista_escuelas = Centros.objects.all()
    
    return render(request, 'index.html', {
        "escuelas":lista_escuelas,
    })

def cargar_escuelas(request):

    # CREAMOS UN CONTADOR QUE AVANCE AUTOMATICAMENTE
    contador = count()
    next(contador)
    # CREAMOS UNA VARIABLE QUE MANTENGA EL BUCLE ACTIVO
    activar_bucle = True

    # CREAMOS UN BUCLE INFINITO PARA RECORRER LAS PAGINAS
    while  activar_bucle == True:

        # HACEMOS UNA PETICION GET A LA PAGINA AÑADIENDO EL NUMERO MEDIANTE EL CONTADOR
        pagina = requests.get('https://www.scholarum.es/es/listado-centros-estiron/%s'%(next(contador)))
        soup = BeautifulSoup(pagina.content, "html.parser")
        # hACEMOS SCRAPPING PARA SACAR EL CUADRO DE ESCUELAS Y LUEGO UNA LISTA CON LAS ESCUELAS
        cuadro_escuelas = soup.find("div", {"id":"ctl00_ContentPlaceHolder1_colegios_destacados"})
        escuelas = cuadro_escuelas.find_all("div", {"class":"registro_colegio_buscador"})
        
        # COMPROBAMOS QUE EXISTEN ESCUELAS EN LA PAGINA DADO QUE PENSABA REALIZARLO
        # CON EL TIPO DE RESPUESTA DEL GET PERO DEVUELVE PAGINAS VACIAS CUANDO
        # SUPERAMOS EL NUMERO DE PAGINAS EXISTENTES
        # DE ESTÁ MANERA CUANDO LA PAGINA ESTÁ EN BLANCO LA LISTA ESTÁ VACIA
        if escuelas:
            # COMPROBAMOS QUE EXTRAE LOS DATOS ADECUADAMENTE
            print('Ok')
        
        else:
            # CUANDO LA LISTA LLEGA VACIA PARAMOS EL BUCLE INFINITO
            activar_bucle = False
            print('__Fin__')
  
    response = redirect('/index')
    return response