from django.contrib import admin

from .models import Gare, Trajet

   
admin.site.register(Trajet)
admin.site.register(Gare)