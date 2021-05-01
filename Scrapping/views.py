from django.shortcuts import render
from django.shortcuts import redirect
from itertools import count
import requests
from bs4 import BeautifulSoup
import re
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

            # CREAMOS UN BUCLE QUE RECORRA CADA ESCUELA DE LA LISTA
            for escuela in escuelas:
                #COMENZAMOS A EXTRAER DATOS
                # EXTRAEMOS LA IMAGEN Y SACAMOS SU SRC
                url_imagen_escuela = escuela.find("img").get("src").encode("ascii", "ignore").decode("utf-8")
                
                # EVITAMOS LA IMAGEN POR DEFETO DE LOS CENTROS SIN IMAGEN
                if url_imagen_escuela == 'img_logo.jpg':
                    imagen_escuela = ''
                else:
                    # AÑADIMOS EL RESTO DE LA URL PARA QUE PUEDAN SER EXTRAIDAS LAS IMAGENES
                    url_imagen_escuela = "https://www.scholarum.es%s"%(url_imagen_escuela)
                    # EXTRAEMOS LA IMAGEN DE LA URL ANTES CREADA
                    imagen_escuela = requests.get(url_imagen_escuela)

                # EXTRAEMOS EL NOMBRE DE LA ESCUELA
                nombre_escuela = escuela.find("h2").text.encode("ascii", "ignore").decode("utf-8")
                # EXTRAEMOS EL TIPO DE CENTRO
                tipo_de_centro = escuela.find("font").text.encode("ascii", "ignore").decode("utf-8")
                # COMO LOS CENTROS PUBLICOS ESTÁN MAL ESCRITOS LOS MODIFICAMOS
                if tipo_de_centro == 'Pblico':
                    tipo_de_centro = 'Publico'

                # COMO LA DIRECCIÓN SE ENCUENTRA EN 2 ETIQUETAS <p> SACAMOS AMBAS
                lita_direcciones_escuela = escuela.find_all("p")
                # DE ESTÁ LISTA SACAMOS PRIMERO LA DIRECCIÓN, LUEGO POBLACIÓN Y CIUDAD
                direccion_escula_1 = str(lita_direcciones_escuela[0]).replace('<p>', '').replace('</p>', '').encode("ascii", "ignore").decode("utf-8")
                direccion_escula_2 = str(lita_direcciones_escuela[1]).replace('<p>', '').replace('</p>', '').encode("ascii", "ignore").decode("utf-8")
                # EN LA PRIMERA DIRECCIÓN SE ENCUENTRA CALLLE, NUMERO Y CODIGO POSTAL
                # COMO EL FORMATO NO ES IGUAL PARA TODAS NO PUEDO CREAR UNA LISTA
                # A PARTIR DE LAS COMAS POR LO QUE VOY A UTILIZAR UN METODO DIFERENTE
                # LO PRIMERO QUE QUIERO OBTENER ES LA CALLE POR LO QUE VOY A LOCALIZAR
                # LA PRIMERA COMA Y EXTRAER LA CALLE CON ESE RESULTADO
                coma_calle = direccion_escula_1.find(",")
                calle_escuela = direccion_escula_1[:coma_calle]
                # EL FORMATO DE TODAS LAS CALLES NO ES IGUAL Y ALGUNAS CONTIENEN NUMEROS
                # KM O OTRO TIPO DE CARACTERES NO DESEADOS, VOY A FORMATEARLO
                # CON ESTO VOY A ELIMINAR LOS NUMEROS DE LA CALLE
                calle_escuela = re.sub(r'[0-9]+', '', calle_escuela)
                # SURGE UN PROBLEMA PORQUE SE ELIMINAN TODOS LOS NUMEROS
                # Y HAY ALGUNOS QUE NO DEBEN BORRARSE PERO LO SOLUCIONARE MÁS ADELANTE
                # ELIMINO CARACTERES NO DESEADOS QUE HE VISTO EN LAS CALLES
                calle_escuela = calle_escuela.replace('s/n', '').replace('Km','').replace('km', '').replace('-yr', '').replace('-', '').replace('(', '').replace(')', '').replace('.', '')
                print(calle_escuela)
        else:
            # CUANDO LA LISTA LLEGA VACIA PARAMOS EL BUCLE INFINITO
            activar_bucle = False
            print('__Fin__')
  
    response = redirect('/index')
    return response