from django.contrib import admin

from .models import Gare, Trajet, Reservation, Client, Passager

   
admin.site.register(Trajet)
admin.site.register(Gare)
admin.site.register(Reservation)
admin.site.register(Client)
admin.site.register(Passager)