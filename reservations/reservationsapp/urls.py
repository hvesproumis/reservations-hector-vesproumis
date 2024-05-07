"""
This file contains all the used urls for the application
"""

from django.urls import path
from . import views

app_name = "reservations"  # This should match the namespace used in the project's urls.py
urlpatterns = [
    # Account related urls
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('update_profile/', views.update_profile, name='update_profile'),
    
    # Reservations related urls
    path('journeys/', views.journeys, name="journeys"),
    path('reservations/', views.reservations, name='reservations'),
    path('reservation/<str:if_number>/', views.reservation_detail, name='reservation_detail'),
    path('new_reservation/', views.edit_reservation, name='create_reservation'),
    path('edit_reservation/<str:if_number>/', views.edit_reservation, name='edit_reservation'),
    path('delete_reservation/<str:if_number>/', views.delete_reservation, name = "delete_reservation"),
    
    # Passengers related urls
    path('create_passenger/', views.create_passager, name='create_passager'),
    path('my_passengers/', views.view_passagers, name='view_passagers'),
    path('edit_passenger/<int:passager_id>/', views.edit_passager, name='edit_passager'),
    path('delete_passenger/<int:passager_id>/', views.delete_passager, name='delete_passager'),
    
    # API endpoints for AJAX operations
    path('api/get-dates-for-route/<int:route_id>/', views.get_dates_for_route, name='get_dates_for_route'),
    path('api/get-trips-for-date/<int:route_id>/<str:date>/', views.get_trips_for_date, name='get_trips_for_date'),
    path('api/get-journeys-for-route/<int:route_id>/<str:date>/', views.get_journeys_for_route, name='get_journeys_for_route'),

    
    # Specific admin urls
    path('api/passengers/<int:passager_id>/', views.get_passager_details, name='get_passager_details'),
    path('api/advanced_search/', views.advanced_search, name='advanced_search'),
    path('advanced_search/', views.advanced_search, name='advanced_search'),
    path('collaborator/', views.collaborator, name='collaborator'),
]
