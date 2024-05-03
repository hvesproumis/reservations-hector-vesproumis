from django.shortcuts import render, get_object_or_404, redirect
from .models import Route, Client, Reservation, Passager, Journey, Ticket
from .forms import TrajetSearchForm, ReservationForm, ClientForm, PassagerForm, SignUpForm, UserUpdateForm
from django.conf import settings
from django.forms import formset_factory
from django.db import transaction
from django.db.models import Count, F, Sum, Q
from django.db.models.functions import TruncDay
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

#Utilisateur

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def account(request):
    return render(request, 'registration/account.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/update_profile.html', {'form': form})

#Trajets

def trajets(request):
    form = TrajetSearchForm(request.GET or None)
    routes = Route.objects.all()

    if form.is_valid():
        choice = form.cleaned_data['choice']
        station = form.cleaned_data['station']
        if choice == 'depart':
            routes = routes.filter(departure_station=station)
        elif choice == 'arrivee':
            routes = routes.filter(arrival_station=station)
        journeys = Journey.objects.filter(route__in=routes).order_by('departure_date_time')

    paginator = Paginator(journeys, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reservationsapp/liste_trajets.html', {'form': form, 'page_obj': page_obj})

#Réservations

@login_required
def reservations(request):
    if request.user.is_staff:
        toutes_les_reservations = Reservation.objects.all()
    else:
        toutes_les_reservations = Reservation.objects.filter(client__user=request.user)
    
    return render(request, 'reservationsapp/liste_reservations.html', {'reservations': toutes_les_reservations})


@login_required
def reservation_detail(request, if_number):
    if request.user.is_staff:
        reservation = get_object_or_404(Reservation, if_number=if_number)
    else:
        reservation = get_object_or_404(Reservation, if_number=if_number, client__user=request.user)

    return render(request, 'reservationsapp/reservation_detail.html', {'reservation': reservation})

@login_required
def edit_reservation(request, if_number=None):
    client, created = Client.objects.update_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or 'Default First Name',
            'last_name': request.user.last_name or 'Default Last Name',
            'email': request.user.email or 'email@example.com',
            'address': 'Entrez votre adresse'
        }
    )

    if if_number:
        reservation = get_object_or_404(Reservation, if_number=if_number, client=client)
        template_name = 'reservationsapp/edit_reservation.html'  
    else:
        reservation = Reservation(client=client)
        template_name = 'reservationsapp/create_reservation.html'  

    client_form = ClientForm(request.POST or None, instance=client)
    reservation_form = ReservationForm(request.POST or None, instance=reservation, user=request.user)

    if request.method == 'POST':
        if client_form.is_valid() and reservation_form.is_valid():
            client = client_form.save()  
            reservation = reservation_form.save(commit=False)
            reservation.client = client  
            reservation.save()
            
            passengers = reservation_form.cleaned_data['passengers']
            for passenger in passengers:
                for journey in reservation.journeys:
                    ticket = Ticket()
                    ticket.reservation = reservation
                    ticket.journey = journey
                    ticket.passenger = passenger
                    ticket.save()
            return redirect('reservation_detail', if_number=reservation.if_number)

    return render(request, template_name, {
        'client_form': client_form,
        'reservation_form': reservation_form
    })


    
#Passagers

def get_passager_details(request, passager_id):
    try:
        passager = Passager.objects.get(id=passager_id, user=request.user)
        data = {
            'first_name': passager.first_name,
            'last_name': passager.last_name,
            'date_of_birth': passager.date_of_birth.strftime('%Y-%m-%d') if passager.date_of_birth else None
        }
        return JsonResponse(data)
    except Passager.DoesNotExist:
        return JsonResponse({'error': 'Passager not found'}, status=404)
    
@login_required
def create_passager(request):
    if request.method == 'POST':
        form = PassagerForm(request.POST)
        if form.is_valid():
            passager = form.save(commit=False)
            passager.user = request.user 
            passager.save()
            return redirect('view_passagers')
    else:
        form = PassagerForm()
    return render(request, 'reservationsapp/create_passager.html', {'form': form})

@login_required
def view_passagers(request):
    passagers = Passager.objects.filter(user=request.user) 
    return render(request, 'reservationsapp/view_passagers.html', {'passagers': passagers})

@login_required
def edit_passager(request, passager_id):
    passager = get_object_or_404(Passager, id=passager_id, user=request.user)
    if request.method == 'POST':
        form = PassagerForm(request.POST, instance=passager)
        if form.is_valid():
            form.save()
            return redirect('view_passagers')
    else:
        form = PassagerForm(instance=passager)
    return render(request, 'reservationsapp/edit_passager.html', {'form': form})

@login_required
def delete_passager(request, passager_id):
    passager = get_object_or_404(Passager, id=passager_id, user=request.user)
    if passager.reservations.exists():
        messages.error(request, "Ce passager est associé à des réservations et ne peut pas être supprimé.")
    else:
        passager.delete()
        messages.success(request, "Passager supprimé avec succès.")
    return redirect('reservationsapp/view_passagers.html')

#Staff view linked to stats view template only accessible to staff members
@staff_member_required
def collaborator(request):
    return render(request, 'admin/statistic_view.html')

#For staff, data on reservations

@staff_member_required
@require_http_methods(["GET"])
def advanced_search(request):
    # Récupérer les paramètres de la requête
    type_search = request.GET.get('type')
    keyword = request.GET.get('keyword')

    if type_search == 'reservations_by_day':
        # Nombre de réservations par jour
        data = Reservation.objects.annotate(day=TruncDay('journey__departure_date_time')).values('day').annotate(count=Count('id')).order_by('day')

    elif type_search == 'reservations_by_route':
        # Nombre de réservations par trajet
        data = Reservation.objects.filter(journey__route=keyword).values('journey__route').annotate(count=Count('id')).order_by('journey__route')

    elif type_search == 'list_reservations':
        # Liste des réservations pour une gare de départ ou d'arrivée
        data = Reservation.objects.filter(Q(journey__depgare=keyword) | Q(journey__arrgare=keyword)).annotate(total_passengers=Sum('passenger_count'))

    elif type_search == 'list_passengers':
        # Liste des passagers pour un trajet
        data = Passager.objects.filter(journey__route=keyword).values('name', 'journey__route')

    elif type_search == 'occupancy_rate':
        # Taux de remplissage d'un trajet
        data = Reservation.objects.filter(journey__route=keyword).aggregate(occupancy_rate=Sum('passenger_count') / 500 * 100)

    elif type_search == 'station_frequency':
        # Taux de fréquentation d'une gare
        data = Reservation.objects.filter(Q(journey__depgare=keyword) | Q(journey__arrgare=keyword)).values('journey__depgare').annotate(frequency=Count('id'))

    else:
        data = {"error": "Invalid search type"}

    return JsonResponse(list(data), safe=False)

#Pour info, utiliser l'API : 
#function performSearch(typeSearch, keyword) {
#    let url = new URL('/api/advanced-search/', window.location.origin);
#    url.searchParams.append('type', typeSearch);
#    url.searchParams.append('keyword', keyword);
#
#    fetch(url)
#    .then(response => response.json())
#    .then(data => {
#       console.log(data); // Traiter et afficher les données
#    })
#    .catch(error => console.error('Error fetching data:', error));
#}
#
#// Exemple d'utilisation
#performSearch('reservations_by_day', '2023-09-01');