from django.shortcuts import render
from django.shortcuts import redirect
from django.core.files import File
from django.templatetags.static import static
from django.core.files.temp import NamedTemporaryFile
from itertools import count
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from vincenty import vincenty
import requests
from django.core.files.uploadedfile import SimpleUploadedFile
import re
import urllib
from .models import Centros

def index(request):

    # CARGAMOS UN LISTADO CON TODS LAS ESCUELAS DE LA BASE DE DATOS
    lista_escuelas = Centros.objects.all()
    # COMPROBAMOS SI RECIBE UNA RESPUESTA POST
    if request.method == 'POST':
        # SACAMOS EL iD DE ESCUELA RECIBIDO EN POST
        id_escuela = request.POST.get('pk')
        # OBTENEMOS LATITUD Y LONGITUD DEL USUARIO
        latitud_usuario = request.POST.get('lati')
        longitud_usuario = request.POST.get('longi')
        # OBTENEMODS LA ESCUELA CON EL ID
        escuela = Centros.objects.get(pk=id_escuela)
        # CREAMOS UN GEOLOCALIZADOR
        geolocator = Nominatim(user_agent="Magister")
        # LE PASAMOS EL CODIGO POSTAL DE LA ESCUELA PARA CONEGUIR UNA DISTNCIA APROXIMADA
        geo1 = geolocator.geocode('%s, españa'%(escuela.codigo))
        # AQUI AÑADIMOS CORDENADAS A LA BASE DE DATOS PARA FUTURAS CONSULTAS
        # AL HACER CLICK EN CADA ESCCUELA
        # PUEDE HACERSE AL CARGAR DATOS PERO RELENTIZA EL PROCESO
        # DE ESTA MANERA QUITAMOS TIEMPO DE ESPERA EN LA CARGA
        # Y VAMOS AÑADIENDO CORDENADAS SEGUN VEMOS CADA ESCUELA
        # PUEDE HACERSE EN CUALQUIERA DE LOS 2 PUNTOS A GUSTO
        escuela.latitud = geo1.latitude
        escuela.longitud = geo1.longitude
        escuela.save()
        # CREAMOS OBJETOS PARA CALCULAR DISTANCIA DESDE EL USUARIO A LA ESCUELA
        cor_geo1 = (geo1.latitude, geo1.longitude)
        cor_geo2 = (float(latitud_usuario), float(longitud_usuario))
        # CALCULAMOS DISTANCIA Y FORMATEAMOS CORRECTAMENTE
        distancia = vincenty(cor_geo1,cor_geo2)
        distancia = '%s Km'%(int(distancia))
        # CREAMOS UNA URL PARA MOSTRAR UN MAPA CON LA UBICACIÓN
        url_mapa = escuela.nombre+', '+escuela.calle+', '+escuela.numero+', '+escuela.pobalcion+', '+escuela.ciudad+', '+escuela.codigo
        
        return render(request, 'escuela.html', {
            "escuela":escuela,
            "distancia":distancia,
            'url':url_mapa,
        })
    
    return render(request, 'escuelas.html', {
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
        a = next(contador)
        # HACEMOS UNA PETICION GET A LA PAGINA AÑADIENDO EL NUMERO MEDIANTE EL CONTADOR
        pagina = requests.get('https://www.scholarum.es/es/listado-centros-estiron/%s'%(a))
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
                url_imagen_escuela = escuela.find("img").get("src")
                # EVITAMOS LA IMAGEN POR DEFETO DE LOS CENTROS SIN IMAGEN
                
                if url_imagen_escuela == '/imagenes/img_logo.jpg':
                    nombre_foto = ''
                else:
                    # AÑADIMOS EL RESTO DE LA URL PARA QUE PUEDAN SER EXTRAIDAS LAS IMAGENES
                    # DESCARGAMOS IMAGEN Y CREAMOS EL NOMBRE PARQA LUEGO MOSTRARLAS
                    barra_foto = url_imagen_escuela.rfind('/')
                    nombre_foto = url_imagen_escuela[barra_foto:].encode("ascii", "ignore").decode("utf-8")
                    url_imagen_escuela = "https://www.scholarum.es%s"%(url_imagen_escuela)
                    myfile = requests.get(url_imagen_escuela)
                    open('static/fotos/%s'%(nombre_foto),'wb').write(myfile.content)
                    myfile.close()
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
                # SACAMOS UN STRING A PARTIR DEL ULTIMO ESPACIO PARA COMPROBAR SI TIENE NUMEROS
                # DADO QUE EN OCASIONES SEPARAN EL NUMERO CON COMA Y OTRAS NO
                ultimo_espacio = calle_escuela.rfind(" ")
                numeros_ultima_palabra = any(map(str.isdigit, calle_escuela[ultimo_espacio:]))
                # SI TIENE NUMEROS QUITAMOS ESA PARTE DE LA CALLE
                ultima_palabra = calle_escuela[ultimo_espacio+1:]
                if numeros_ultima_palabra == True or ultima_palabra == 's/n':
                    calle_escuela = calle_escuela[:ultimo_espacio]
                # EVITAMOS BORRAR LOS NUMEROS DE LAS CARRETERAS
                if 'Carretera' in calle_escuela:
                    if  'M-' in ultima_palabra or 'A-' in ultima_palabra:
                        calle_escuela = calle_escuela + " " +ultima_palabra
                # ELIMINO CARACTERES NO DESEADOS QUE HE VISTO EN LAS CALLES
                # ESTO SOLO VALE PARA DAR UN MEJOR FORMATO EN ESTAS ESCUELAS
                # DADO QUE LA FORMA DE PRESENTAR LOS DATOS DE LA PAGINA NO ES LA IDONEA
                # PARA NUEVAS ESCUELAS PUEDEN IRSE AÑADIENDO CARACERES O NO USARLO SI ESTA BIEN ESTRUCTURADO
                calle_escuela = calle_escuela.replace('(km.','').replace(' km','').replace(' Km','').replace(' c/', '').replace(' Urb. ', '').replace('Calle Avda/', 'Avenida').replace('Calle Pz.', 'Plaza').replace('Calle Carretera', 'Carretera').replace('Logroo', 'Logroño').replace('Espaa', 'España').replace(' (. )', '').replace('N . ', '')
                # ELIMINAMOS LOS ESPACIOS FINALES SOBRANTES
                calle_escuela = re.sub(r"\s+$", "", calle_escuela)
                # BORRAMOS CARACTERES NO DESEADOS DEL FINAL DE LA CADENA
                largo_calle_escuela = len(calle_escuela)
                if calle_escuela[largo_calle_escuela-2:largo_calle_escuela] == ' n' or calle_escuela[largo_calle_escuela-2:largo_calle_escuela] == ' N' or calle_escuela[largo_calle_escuela-2:largo_calle_escuela] == ' K' or calle_escuela[largo_calle_escuela-2:largo_calle_escuela] == ' -' or calle_escuela[largo_calle_escuela-2:largo_calle_escuela] == ' B':
                    calle_escuela = calle_escuela[:largo_calle_escuela-2]
                # QUITAMOS LAS CALLES QUE NO CONSTAN
                if 'No Consta' in calle_escuela:
                    calle_escuela = ''
                # EXTRAEMOS UNA LISTA DE TODOS LOS NUMEROS DE LA DIRECCIÓN
                lista_numeros = re.split('\D+', direccion_escula_1)
                # HACEMOS EL ARREGLO ANTERIOMENTE MENCIONADO Y EXTRAER EL NUMERO
                # COMPROBAMOS SI NO TIENE NUMERO Y LE DAMOS ESE FORMATO AL NUMERO
                if 's/n' in direccion_escula_1:
                    numero_escuela = ''
                # COMO LA LISTA DE NUMEROS PUEDE VARIAR DE LONGITUD LO CALCULAMOS
                # SACANDO EL NUMERO CORRESPONDIENTE
                
                elif len(lista_numeros)>=3 and not 'km' in lista_numeros and not 's/n' in lista_numeros:
                    
                # COMPROBAMOS SI TIENE VARIOS NUMREROS Y LO FORMATEAMOS
                    if '%s-'%(lista_numeros[1]) in direccion_escula_1 or '%s - '%(lista_numeros[1]) in direccion_escula_1 and not '-yr' in direccion_escula_1:
                        
                        numero_escuela = '%s-%s'%(lista_numeros[1],lista_numeros[2])
                    elif lista_numeros[1] in calle_escuela:
                        numero_escuela =lista_numeros[2]
                    else:
                        numero_escuela =lista_numeros[1]
                else:
                    numero_escuela = ''
                # COMPRUEBO SI ES UNA CARRETERA EN LUGAR DE UNA CALLE
                # DE SER ASÍ LA FORMATEO ADECUADAMENTE EL NUMERO EN KM
                if 'M-' in direccion_escula_1 or 'A-' in direccion_escula_1:
                    
                    prueba = lista_numeros[2]+','+lista_numeros[3]
                    if prueba in direccion_escula_1 and len(lista_numeros[3]) == 1:
                        numero_escuela = 'km-%s,%s'%(lista_numeros[2],lista_numeros[3])
                    else:
                        numero_escuela = 'km-%s'%(lista_numeros[2])
                elif 'km' in direccion_escula_1 or 'Km' in direccion_escula_1:
                    prueba = lista_numeros[1]+','+lista_numeros[2]
                    if prueba in direccion_escula_1 and len(lista_numeros[2]) == 1:
                        numero_escuela = 'km-%s,%s'%(lista_numeros[1],lista_numeros[2])
                    else:
                        numero_escuela = 'km-%s'%(lista_numeros[1])
                # SI ALGUNA CALLE TIENE EL NUMERO DENTRO DE LA PRIMERA COMA LO SACAMOS
                # Y CORTAMOS EL ESTRING HASTA ESE PUNTO
                if numero_escuela != '' and numero_escuela in calle_escuela:
                    distancia_numero = calle_escuela.find(numero_escuela)
                    calle_escuela = calle_escuela[0:distancia_numero-2]
                    calle_escuela = re.sub(r"\s+$", "", calle_escuela)
                # EXTRAEMOS EL CODIGO POSTAL QUE SE ENCUENTRA EN 
                # LA ULTIMA POSICIÓN DE LA LISTA DE NUMEROS
                codigo_postal_escuela = lista_numeros[len(lista_numeros)-1]
                # AHORA SACAMOS LA POBLACIÓN Y LA CIUDAD
                coma_poblacion = direccion_escula_2.find(",")
                poblacion_escuela = direccion_escula_2[:coma_poblacion].title()
                ciudad_escuela = direccion_escula_2[coma_poblacion+2:].replace('(', '').replace(')', '').title()
                
                # CREAMOS EL CENTRO, AÑADIMOS PARAMETROS Y GUARDAMOS
                '''DESCOMENTAR LINEAS PARA GUARDAR LATITUD Y LONGITUD
                   ESTO CAUSA UN INCREMENTO COSNSIDERABE EN EL TIEMPO DE CARGA
                   EN SU DEFECTO LO HE COLOCADO AL ABRIR LA ESCUELA

                #geolocator = Nominatim(user_agent="Magister")
                #geo = geolocator.geocode('%s, españa'%(codigo_pos))'''

                if  nombre_escuela:
                    centro = Centros.objects.create()
                    centro.nombre = nombre_escuela
                    centro.foto = nombre_foto
                    centro.direccion = direccion_escula_1+', '+direccion_escula_2+'.'
                    centro.calle = calle_escuela
                    centro.numero = numero_escuela
                    centro.pobalcion = poblacion_escuela
                    centro.ciudad = ciudad_escuela
                    centro.tipo = tipo_de_centro
                    centro.codigo = codigo_postal_escuela
                    #centro.latitud = geo.latitude
                    #centro.longitud = geo.longitude
                    centro.save()
                    print(centro.nombre+" - OK")

                
        else:
            # CUANDO LA LISTA LLEGA VACIA PARAMOS EL BUCLE INFINITO
            activar_bucle = False
            print('__Fin__')
  
    response = redirect('/index')
    return response