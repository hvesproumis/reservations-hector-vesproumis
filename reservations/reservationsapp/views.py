from django.shortcuts import render, get_object_or_404
from .models import Trajet, Reservation
from .forms import TrajetSearchForm
from django.conf import settings
from django.contrib.auth.decorators import login_required



def trajets(request):
    form = TrajetSearchForm(request.GET or None)
    tous_les_trajets = Trajet.objects.all()  # Initialise avec tous les trajets
    
    if form.is_valid():
        choix = form.cleaned_data.get('choix')
        gare = form.cleaned_data.get('gare')
        
        if gare:  # Ajoute un contrôle pour s'assurer que gare n'est pas None
            if choix == 'depart':
                tous_les_trajets = tous_les_trajets.filter(depgare=gare)
            elif choix == 'arrivee':
                tous_les_trajets = tous_les_trajets.filter(arrgare=gare)

    return render(request, 'reservationsapp/liste_trajets.html', {'trajets': tous_les_trajets, 'form': form})

@login_required
def reservations(request):
    if request.user.is_staff:
        toutes_les_reservations = Reservation.objects.all()
    else:
        toutes_les_reservations = Reservation.objects.filter(client__email=request.user.email)
    
    return render(request, 'reservationsapp/liste_reservations.html', {'reservations': toutes_les_reservations})


@login_required
def reservation_detail(request, if_number):
    if request.user.is_staff:
        reservation = get_object_or_404(Reservation, if_number=if_number)
    else:
        reservation = get_object_or_404(Reservation, if_number=if_number, client__email=request.user.email)

    return render(request, 'reservationsapp/reservation_detail.html', {'reservation': reservation})
