from django.shortcuts import render, get_object_or_404, redirect
from .models import Route, Client, Reservation, Passager, Journey
from .forms import TrajetSearchForm, ReservationForm, ClientForm, PassagerForm, SignUpForm, UserUpdateForm
from django.conf import settings
from django.forms import formset_factory
from django.db import transaction
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
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
    tous_les_trajets = Trajet.objects.all().order_by('depdh')

    if form.is_valid():
        choix = form.cleaned_data['choix']
        gare = form.cleaned_data['gare']
        if choix == 'depart':
            tous_les_trajets = tous_les_trajets.filter(depgare=gare)
        elif choix == 'arrivee':
            tous_les_trajets = tous_les_trajets.filter(arrgare=gare)

    paginator = Paginator(tous_les_trajets, 10)
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
            reservation.passager = reservation_form.cleaned_data['existing_passager']
            reservation.save()
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
def number_of_reservation(request):
     # Count reservations for a spec date
    reservations_by_date = Reservation.objects.annotate(
        date=TruncDate('journey__depdh')
    ).values('date').annotate(count=Count('id')).order_by('date')

    # Count reservations for a spec route
    reservations_by_route = Reservation.objects.annotate(
        route=F('journey__route'),
        depgare=F('journey__depgare'),
        arrgare=F('journey__arrgare')
    ).values('route', 'depgare', 'arrgare').annotate(count=Count('id')).order_by('route')

    # Data for answer
    data_by_date = {res['date'].strftime("%Y-%m-%d"): res['count'] for res in reservations_by_date}
    data_by_route = {f"{res['depgare']} à {res['arrgare']}": res['count'] for res in reservations_by_route}

    # To sets of data in one
    data = {
        'reservations_by_date': data_by_date,
        'reservations_by_route': data_by_route
    }

    return JsonResponse(data)