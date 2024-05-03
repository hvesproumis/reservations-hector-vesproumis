from django.contrib import admin
from django.urls import path, include
from reservationsapp import views
from django.contrib.auth import views as auth_views
from reservationsapp.views import get_passager_details, create_passager, view_passagers, edit_passager, delete_passager, signup, update_profile, account, collaborator, advanced_search


urlpatterns = [
    path("admin/", admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path("journeys/", views.journeys, name="journeys"),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reservations/', views.reservations, name='reservations'),
    path('reservation/<str:if_number>/', views.reservation_detail, name='reservation_detail'),
    path('new_reservation/', views.edit_reservation, name='create_reservation'),
    path('edit_reservation/<str:if_number>/', views.edit_reservation, name='edit_reservation'),
    path('create_passenger/', views.create_passager, name='create_passager'),
    path('my_passengers/', views.view_passagers, name='view_passagers'),
    path('edit_passenger/<int:passager_id>/', views.edit_passager, name='edit_passager'),
    path('delete_passenger/<int:passager_id>/', views.delete_passager, name='delete_passager'),
    path('api/passengers/<int:passager_id>/', views.get_passager_details, name='get_passager_details'),
    path('api/advanced_search/', views.advanced_search, name='advanced_search'),
    path('collaborator/', views.collaborator, name='collaborator'),
]