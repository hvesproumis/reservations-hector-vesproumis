
"""
Ce fichier contient toutes les vues et la logique pour faire fonctionner l'application
"""
import random
import pandas
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from .models import Client, Reservation, Passager, Journey, Ticket, Route, Station
from .forms import JourneySearchForm, ReservationForm, ClientForm, PassagerForm, SignUpForm, UserUpdateForm
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth import login
from django.core import serializers
from django.core.serializers import serialize
from django.contrib import messages
from django.utils.dateparse import parse_date
from .algorithms2 import Graph


# User

def signup(request):
    """
    Une vue pour inscrire un nouveau client en utilisant un formulaire prédéfini.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            login(request, user)
            return redirect('/accounts/login/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def account(request):
    """
    Une vue pour afficher les informations du compte d'un client.
    """
    return render(request, 'registration/account.html')

@login_required
def update_profile(request):
    """
    Une vue pour modifier les informations d'un client en fonction du formulaire de mise à jour de l'utilisateur.
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('reservations:account')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/update_profile.html', {'form': form})


# Journeys

def journeys(request):
    form = JourneySearchForm(request.GET or None)
    best_route = None  # Initialize best_route
    journeys = Journey.objects.all().order_by('departure_date_time')

    if form.is_valid():
        departure_station = form.cleaned_data.get('departure_station')
        arrival_station = form.cleaned_data.get('arrival_station')
        depart_date_time = form.cleaned_data.get('depart_date_time')

        # Apply filters based on form inputs
        if departure_station:
            journeys = journeys.filter(route__departure_station=departure_station)
        if arrival_station:
            journeys = journeys.filter(route__arrival_station=arrival_station)
        if depart_date_time:
            journeys = journeys.filter(departure_date_time__date=depart_date_time.date())

        # Check for an optimal path only if both stations and date are specified
        if departure_station and arrival_station and depart_date_time:
            graph = Graph(departure_station, arrival_station, depart_date_time)
            best_route = graph.find_optimal_path(departure_station, arrival_station)

    paginator = Paginator(journeys, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reservationsapp/list_journeys.html', {
        'form': form,
        'page_obj': page_obj,
        'best_route': best_route
    })



# Reservations

@login_required
def reservations(request):
    """
    Une vue utilisée pour afficher toutes les réservations effectuées par un client.
    Si le client est un administrateur, toutes les réservations du site lui sont montrées.
    """
    if request.user.is_staff:
        reservations = Reservation.objects.select_related('client').prefetch_related('journeys')
    else:
        reservations = Reservation.objects.filter(client__user=request.user)
    
    context = {
        'reservations' : reservations,
    }
    return render(request, 'reservationsapp/liste_reservations.html', context=context)


@login_required
def reservation_detail(request, if_number):
    """
    Une vue qui affiche les informations d'une réservation à son client.
    Un administrateur peut voir toutes les réservations.

    Args:
        if_number (Char): L'identifiant de la réservation 
    """
    if request.user.is_staff:
        reservation = get_object_or_404(Reservation, if_number=if_number)
    else:
        reservation = get_object_or_404(Reservation, if_number=if_number, client__user=request.user)

    tickets = Ticket.objects.filter(reservation=reservation).order_by("journey")
    context = {
        'reservation' : reservation,
        'tickets' : tickets,
    }
    
    return render(request, 'reservationsapp/reservation_detail.html', context=context)


@login_required
def edit_reservation(request, if_number=None):
    """
    View for creating or updating a reservation using the ReservationForm.

    Args:
    if_number (str, optional): The identifier of the reservation that the client wants to edit.
    Default is None, which means a new reservation is being created.
    """
    user = request.user
    client, created = Client.objects.get_or_create(user=user)

    if if_number:
        reservation = get_object_or_404(Reservation, if_number=if_number, client=client)
        template_name = 'reservationsapp/edit_reservation.html'
    else:
        reservation = Reservation(client=client)
        template_name = 'reservationsapp/create_reservation.html'

    client_form = ClientForm(request.POST or None, instance=client)
    reservation_form = ReservationForm(request.POST or None, instance=reservation, user=user)

    if request.method == 'POST':
        if client_form.is_valid() and reservation_form.is_valid():
            client_form.save()
            reservation = reservation_form.save(commit=False)
            reservation.client = client
            reservation.save()
            reservation_form.save_m2m()  # To save many-to-many data for passengers and journeys

            return redirect('reservations:reservation_detail', if_number=reservation.if_number)

    routes = Route.objects.all()
    stations = Station.objects.all()
    serialized_stations = serialize("json", stations)

    return render(request, template_name, {
        'client_form': client_form,
        'reservation_form': reservation_form,
        'routes': routes,
        'stations': serialized_stations
    })

@login_required
def delete_reservation(request, if_number):
    """
    Une vue pour supprimer une réservation.

    Args:
        if_number (Char): L'identifiant de la réservation.
    """
    reservation = get_object_or_404(Reservation, if_number=if_number, client=request.user.client)
    reservation.delete()
    messages.success(request, "Réservation annulée avec succès.")
    return redirect('reservations:reservations')

@login_required
def create_passager(request):
    """
    Une vue utilisée pour créer un nouveau passager associé au client qui ouvre la vue, en utilisant le formulaire Passenger.
    """
    if request.method == 'POST':
        form = PassagerForm(request.POST)
        if form.is_valid():
            passager = form.save(commit=False)
            passager.user = request.user 
            passager.save()
            return redirect('reservations:view_passagers')
    else:
        form = PassagerForm()
    return render(request, 'reservationsapp/create_passager.html', {'form': form})

@login_required
def view_passagers(request):
    """
    Une vue pour afficher tous les passagers appartenant à un client.
    """
    passagers = Passager.objects.filter(user=request.user) 
    return render(request, 'reservationsapp/view_passagers.html', {'passagers': passagers})

@login_required
def edit_passager(request, passager_id):
    """
    Une vue pour modifier les informations d'un passager en utilisant le formulaire Passenger.

    Args:
        passager_id (int): L'identifiant du passager.
    """
    passager = get_object_or_404(Passager, id=passager_id, user=request.user)
    if request.method == 'POST':
        form = PassagerForm(request.POST, instance=passager)
        if form.is_valid():
            form.save()
            return redirect('reservations:view_passagers')
    else:
        form = PassagerForm(instance=passager)
    return render(request, 'reservationsapp/edit_passager.html', {'form': form})

def get_passager_details(request, passager_id):
    """
    A view only used to return a JSON with the passenger information.

    Args:
        passager_id (Int): The id of the pasenger
    """
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
def delete_passager(request, passager_id):
    """
    Une vue pour supprimer un passager.

    Args:
        passager_id (Int): L'identifiant du passager.
    """
    if request.user.is_staff:
        passager = get_object_or_404(Passager, id=passager_id)
    else:
        passager = get_object_or_404(Passager, id=passager_id, user=request.user)
    if passager.tickets.exists():
        messages.error(request, "Ce passager est associé à des réservations et ne peut pas être supprimé.")
    else:
        passager.delete()
        messages.success(request, "Passager supprimé avec succès.")
    return redirect('reservations:view_passagers')

@staff_member_required
def collaborator(request):
    """
    Une vue utilisée pour afficher des informations statistiques pour un administrateur de site.
    Elle repose sur la vue 'advanced_search' pour interroger les données pour les graphiques.
    """
    return render(request, 'admin/statistics_view.html')

@staff_member_required
@require_http_methods(["GET"])
def advanced_search(request):
    """
    A view used to return statistical data (JSON) based on keywords and the type of the request.
    The information are then processed in a template to create a chart.
    """
    type_search = request.GET.get('type')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    keyword = request.GET.get('keyword', '')
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    # get all days between start_date and end_date
    days = pandas.date_range(start_date,end_date-timedelta(days=1),freq='d').date.tolist()

    # Dictionary containing optional keys for the chart, depending on the the chart wanted
    options = {}
    
    
    if type_search == 'reservations_by_day':
        chart_type = 'line'
        title = 'Nombre de réservations effectuées par jour'
        subtitle = ''
        xAxis = {
            'tickInterval': 7 * 24 * 3600 * 1000, # one week
            'tickWidth': 0,
            'gridLineWidth': 1,
            'labels': {
                'align': 'left',
                'x': 3,
                'y': -3
            },
            'title' : {'text': 'Date'}
        }
        yAxis = {
            'allowDecimals': False,
            'title': {'text': 'Nombre de réservations'}
        }
        
        dataset = Reservation.objects.annotate(day=TruncDay('reservation_date')).values('day').annotate(count=Count('id')).order_by('day')
        rows = {} # utilitary dict to find easily a row using the day associated to it
        for row in dataset:
            rows[row['day']] = row['count']

        data = []
        # If the day is present in rows, there were at least one reservation that day, if not, the number of reservations that day is zero
        for day in days :
            if day in rows.keys():
                data.append({'name': day.strftime('%Y-%m-%d'), 'y': rows[day]})
            else :
                data.append({'name': day.strftime('%Y-%m-%d'), 'y': 0})
            
        series = [{'name': 'Réservations', 'data': data}]
        
        options['legend'] = {'enabled': False}


    elif type_search == 'reservations_by_route':
        queryset = Ticket.objects.filter(
            journey__departure_date_time__gte=start_date,
            journey__departure_date_time__lte=end_date
        ).values(
            'journey__route__departure_station__city',
            'journey__route__arrival_station__city'
        ).annotate(count=Count('id')).order_by('journey__route__departure_station__city')

        data = [{'name': f"{row['journey__route__departure_station__city']} - {row['journey__route__arrival_station__city']}", 'y': row['count']} for row in queryset]
        series = [{'name': 'Nombre de réservations sur cette route', 'data': data}]

        chart_type ='pie'
        title = 'Nombre de réservations par route'
        subtitle = ''
        xAxis = {'type': 'category'}
        yAxis = {'title': {'text': 'Nombre de réservations'}, 'allowDecimals': False},
        options['legend'] = {'enabled': False}
        
        options['plotOptions'] = {
            'pie': {
                'allowPointSelect': True,
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': True,
                    'format': '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        }

    
    elif type_search == 'occupancy_rate':
        chart_type = 'column'
        title = f'Taux de remplissage par trajets, entre le {start_date} et le {end_date}'
        subtitle = ''
        xAxis = {'type': 'category'}
        yAxis = {
            'allowDecimals': False,
            'title': {'text': 'Taux de remplissage'}
        }
        
        maximum = 100 #14 * 120. = Number of cars * number of seats = max space in a train, let at 100 here for demonstration purposes
        routes = Route.objects.all()
        series = []
        for route in routes :
            data = []
            journeys = Journey.objects.all().filter(route=route).filter(
            departure_date_time__gte=start_date,
            departure_date_time__lte=end_date)
            for journey in journeys :
                dataset = Ticket.objects.all().filter(journey=journey).count() * (100. / maximum)
                data.append({'name': journey.departure_date_time.strftime('%Y-%m-%d %H:%m'), 'y': dataset})
            series.append({'name': f"{route.departure_station}-{route.arrival_station}", 'data': data, 'visible':False})
        
    elif type_search == 'station_frequency':
        chart_type = 'column'
        title = f'Taux de passage par une gare, entre le {start_date} et le {end_date}'
        subtitle = ''
        xAxis = {'type': 'category'}
        yAxis = {
            'allowDecimals': False,
            'title': {'text': 'Voyageurs'}
        }
        
        stations = Station.objects.all()
        series = []
        for station in stations :
            tickets_arriving = Ticket.objects.all().filter(
            journey__departure_date_time__gte=start_date,
            journey__departure_date_time__lte=end_date).filter(journey__route__arrival_station=station).count()
            
            tickets_departing =  Ticket.objects.all().filter(
            journey__departure_date_time__gte=start_date,
            journey__departure_date_time__lte=end_date).filter(journey__route__departure_station=station).count()
            data = [
                {'name': "Départs", 'y': tickets_departing},
                {'name': "Arrivées", 'y': tickets_arriving}
            ]
            series.append({'name': f"{station}", 'data': data, 'visible':False})

    # WIP functionnalities
    #
    #elif type_search == 'list_reservations':
    #    data = list(Reservation.objects.filter(Q(route__departure_station=keyword) | Q(route__arrival_station=keyword)).annotate(total_passengers=Sum('passenger_count')))
    #    return JsonResponse(data)
    #
    #elif type_search == 'list_passengers':
    #    data = Passager.objects.filter(journey__route=keyword).values('name', 'journey__route')
    #    return JsonResponse(data) 

    else:
        return JsonResponse({}) 
    
    chart = {
        'chart': {'type': chart_type},
        'title': {'text': title},
        'subtitle': subtitle,
        'xAxis': xAxis,
        'yAxis': yAxis,
        'series': series
    } | options
    
    return JsonResponse(chart)

#API

def get_dates_for_route(request, route_id):
    """ Returns a list of unique dates when journeys are scheduled for a given route """
    dates = Journey.objects.filter(route_id=route_id).dates('departure_date_time', 'day').distinct()
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    return JsonResponse({'dates': dates})

def get_trips_for_date(request, route_id, date):
    """ Returns journeys for a given route and date """
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    journeys = Journey.objects.filter(route_id=route_id, departure_date_time__date=date_obj)
    trips = [{'id': journey.id, 'departure_time': journey.departure_date_time.strftime('%H:%M'), 'arrival_time': journey.arrival_date_time.strftime('%H:%M')} for journey in journeys]
    return JsonResponse({'trips': trips})

def get_journeys_for_route(request, route_id, date):
    """
    Renvoie les trajets disponibles pour une route et une date données.
    """
    journeys = Journey.objects.filter(route_id=route_id, departure_date_time__date=date).order_by('departure_date_time')
    data = [{
        'id': journey.id,
        'departure_time': journey.departure_date_time.strftime('%Y-%m-%d %H:%M'),
        'arrival_time': journey.arrival_date_time.strftime('%Y-%m-%d %H:%M')
    } for journey in journeys]
    return JsonResponse(data, safe=False)
