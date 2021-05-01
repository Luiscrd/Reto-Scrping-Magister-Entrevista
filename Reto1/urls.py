from django.contrib import admin
from django.urls import path
from Scrapping.views import index, cargar_escuelas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index),
    path('cargar/', cargar_escuelas),
]
