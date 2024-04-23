from django.contrib import admin
from django.urls import path, include
from reservationsapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("trajets/", views.trajets, name="trajets"),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reservations/', views.reservations, name='reservations'),
   path('reservation/<str:if_number>/', views.reservation_detail, name='reservation_detail'),
]