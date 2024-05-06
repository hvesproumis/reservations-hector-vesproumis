from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Station, Journey, Route, Reservation, Client, Passager, Ticket


class JourneyAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Départ", {"fields" : ["departure_station", "departure_date_time"]}),
        ("Arrivée", {"fields" : ["arrival_station", "arrival_date_time"]}),
    ]

class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1

class ReservationAdmin(admin.ModelAdmin):
    fields = ["journeys", "client"]
    inlines = [TicketInLine]
    
class TicketAdmin(admin.ModelAdmin):
    fields = ["reservation", "journey", "passenger", "seat", "car"]
    
class ClientAdmin(admin.ModelAdmin):
    fields = ["user", "address"]

   
admin.site.register(Journey)
admin.site.register(Route)
admin.site.register(Station)
admin.site.register(Reservation,ReservationAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Passager)
admin.site.register(Ticket, TicketAdmin)