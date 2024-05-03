from django.contrib import admin

from .models import Gare, Journey, Route, Reservation, Client, Passager

   
admin.site.register(Journey)
admin.site.register(Route)
admin.site.register(Gare)
admin.site.register(Reservation)
admin.site.register(Client)
admin.site.register(Passager)