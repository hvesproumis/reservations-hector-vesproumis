from django.contrib import admin
from django.urls import path, include
from reservationsapp import views
from django.contrib.auth import views as auth_views
from reservationsapp.views import get_passager_details, create_passager, view_passagers, edit_passager, delete_passager, signup, update_profile, account, collaborator, advanced_search


urlpatterns = [
    path("admin/", admin.site.urls),
    path('signup/', signup, name='signup'),
    path('account/', account, name='account'),
    path('update_profile/', update_profile, name='update_profile'),
    path("trajets/", views.trajets, name="trajets"),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reservations/', views.reservations, name='reservations'),
    path('reservation/<str:if_number>/', views.reservation_detail, name='reservation_detail'),
    path('nouvelle_reservation/', views.edit_reservation, name='create_reservation'),
    path('modif_reservation/<str:if_number>/', views.edit_reservation, name='edit_reservation'),
    path('create-passager/', create_passager, name='create_passager'),
    path('mes-passagers/', view_passagers, name='view_passagers'),
    path('edit-passager/<int:passager_id>/', edit_passager, name='edit_passager'),
    path('delete-passager/<int:passager_id>/', delete_passager, name='delete_passager'),
    path('api/passagers/<int:passager_id>/', get_passager_details, name='get_passager_details'),
    path('api/advanced-search/', advanced_search, name='advanced_search'),
    path('collaborator/', collaborator, name='collaborator'),
]