from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView


urlpatterns = [
    path('reservations/', include('reservationsapp.urls', namespace='reservations')),  # Corrected namespace
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^$', RedirectView.as_view(url='/reservations/journeys', permanent=True)),
]
