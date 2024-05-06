import random
from django.shortcuts import render, get_object_or_404, redirect
from .models import Route, Client, Reservation, Passager, Journey, Ticket, Station
from .forms import JourneySearchForm, ReservationForm, ClientForm, PassagerForm, SignUpForm, UserUpdateForm
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
from .algorithms import Graph
from django.contrib import messages
from django.utils.dateparse import parse_date

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
            return redirect('/accounts/login/')
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
            return redirect('reservations:account')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/update_profile.html', {'form': form})

#Trajets

def journeys(request):
    """
        ->User can look for routes linked to a departure, arrival or both
        ->if both departure and arrival provided, best options are filtered

    """
    form = JourneySearchForm(request.GET or None)
    journeys = Journey.objects.select_related('route').all().order_by('departure_date_time')

    if form.is_valid():
        choice = form.cleaned_data['choice']
        station = form.cleaned_data['station']
        if choice == 'depart':
            journeys = journeys.filter(route__departure_station=station)
        elif choice == 'arrivee':
            journeys = journeys.filter(route__arrival_station=station)

        start_point = form.cleaned_data.get("depart")
        end_point = form.cleaned_data.get("arrivee")
        best_route = None

        if start_point and end_point:  # Check that both points are provided
            #Generate a distance graph
            graph_distance = Graph("distance") #later include same but with cost etc.
            graph_distance.generate_graph()

            try:
                # Solve for the best route (shortest path)
                best_route = graph_distance.solve_graph_shortest_path(start_point, end_point)
            except Exception as e:
                print(f"Error finding shortest path: {e}")
                
        if best_route:
            return render(request, 'reservationsapp/liste_journeys.html', {'form': form, 'page_obj': page_obj, 'best_route': best_route})

    paginator = Paginator(journeys, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reservationsapp/list_journeys.html', {'form': form, 'page_obj': page_obj})

#Réservations

@login_required
def reservations(request):
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
    if request.user.is_staff:
        reservation = get_object_or_404(Reservation, if_number=if_number)
    else:
        reservation = get_object_or_404(Reservation, if_number=if_number, client__user=request.user)

    tickets = Ticket.objects.all().filter(reservation=reservation).order_by("journey")
    context = {
        'reservation' : reservation,
        'tickets' : tickets,
    }
    
    return render(request, 'reservationsapp/reservation_detail.html', context=context)

@login_required
def edit_reservation(request, if_number=None):
    # Initialize variables
    template_name = 'reservationsapp/create_reservation.html'
    user = request.user
    client, created = Client.objects.get_or_create(user=user)

    # Fetch or initialize the reservation
    if if_number:
        reservation = get_object_or_404(Reservation, if_number=if_number, client=client)
        template_name = 'reservationsapp/edit_reservation.html'
    else:
        reservation = Reservation(client=client)

    # Prepare forms
    client_form = ClientForm(request.POST or None, instance=client)
    reservation_form = ReservationForm(request.POST or None, instance=reservation, user=request.user)

    if request.method == 'POST':
        if client_form.is_valid() and reservation_form.is_valid():
            # Save forms
            client_form.save()
            reservation = reservation_form.save(commit=False)
            reservation.client = client
            reservation.save()

            # Handle tickets (deletion and re-creation)
            Ticket.objects.filter(reservation=reservation).delete()
            passengers = reservation_form.cleaned_data['passengers']
            journeys = reservation_form.cleaned_data['journeys']
            for passenger in passengers:
                for journey in journeys:
                    Ticket.objects.create(
                        reservation=reservation,
                        journey=journey,
                        passenger=passenger,
                        car=random.randint(1, 14),
                        seat=random.randint(1, 120)
                    )
            return redirect('reservations:reservation_detail', if_number=reservation.if_number)

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
            return redirect('reservations:view_passagers')
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
            return redirect('reservations:view_passagers')
    else:
        form = PassagerForm(instance=passager)
    return render(request, 'reservationsapp/edit_passager.html', {'form': form})

@login_required
def delete_passager(request, passager_id):
    passager = get_object_or_404(Passager, id=passager_id, user=request.user)
    if passager.tickets.exists():
        messages.error(request, "Ce passager est associé à des réservations et ne peut pas être supprimé.")
    else:
        passager.delete()
        messages.success(request, "Passager supprimé avec succès.")
    return redirect('reservations:view_passagers')

#Staff view linked to stats view template only accessible to staff members
@staff_member_required
def collaborator(request):
    type = 'reservations_by_day'
    keyword = ''
    context = {
        'type' : type,
        'keyword' : keyword
    }
    return render(request, 'admin/statistics_view.html', context=context)

#For staff, data on reservations

@staff_member_required
@require_http_methods(["GET"])
def advanced_search(request):
    type_search = request.GET.get('type')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    keyword = request.GET.get('keyword', '')
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)

    # Dictionary containing optional keys for the chart, depending on the the chart wanted
    options = {}
    
    if type_search == 'reservations_by_day':
        chart_type = 'column'
        title = 'Nombre de réservations effectuées par jour'
        subtitle = ''
        xAxis = {'type': 'category'}
        yAxis = {
            'allowDecimals': 'false',
            'title': {'text': 'Nombre de réservations'}
        }
        
        dataset = Reservation.objects.annotate(day=TruncDay('reservation_date')).values('day').annotate(count=Count('id')).order_by('day')
        data = [{'name': row['day'].strftime('%Y-%m-%d'), 'y': row['count']} for row in dataset]
        series = [{'name': 'Réservations', 'data': data}]
        options['legend'] = {'enabled': 'false'}

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

        chart = {
            'chart': {'type': 'column'},
            'title': {'text': 'Nombre de réservations par route'},
            'xAxis': {'type': 'category'},
            'yAxis': {'title': {'text': 'Nombre de réservations'}, 'allowDecimals': False},
            'series': series,
            'legend': {'enabled': False}
        }
        return JsonResponse(chart)


    
    elif type_search == 'list_reservations':
        data = list(Reservation.objects.filter(Q(route__departure_station=keyword) | Q(route__arrival_station=keyword)).annotate(total_passengers=Sum('passenger_count')))
        data = list(Reservation.objects.filter(Q(route__departure_station=keyword) | Q(route__arrival_station=keyword)).annotate(total_passengers=Sum('passenger_count')))

    elif type_search == 'list_passengers':
        data = Passager.objects.filter(journey__route=keyword).values('name', 'journey__route')

    elif type_search == 'occupancy_rate':
        data = Reservation.objects.filter(journey__route=keyword).aggregate(occupancy_rate=Sum('passenger_count') / 500 * 100)

    elif type_search == 'station_frequency':
        data = Reservation.objects.filter(Q(route__departure_station=keyword) | Q(route__arrival_station=keyword)).values('journey__depgare').annotate(frequency=Count('id'))

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