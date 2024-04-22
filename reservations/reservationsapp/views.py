from django.shortcuts import render
from .models import Trajet
from .forms import TrajetSearchForm

def trajets(request):
    form = TrajetSearchForm(request.GET or None)
    if form.is_valid():
        choix = form.cleaned_data['choix']
        gare = form.cleaned_data['gare']
        if choix == 'depart':
            tous_les_trajets = Trajet.objects.filter(depgare=gare)
        else:
            tous_les_trajets = Trajet.objects.filter(arrgare=gare)
    else:
        tous_les_trajets = Trajet.objects.all()

    return render(request, 'reservationsapp/liste_trajets.html', {'trajets': tous_les_trajets, 'form': form})
