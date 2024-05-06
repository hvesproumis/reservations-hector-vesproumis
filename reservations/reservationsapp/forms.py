"""
This file contains custom forms used in the different views
"""

from django import forms
from .models import Station, Reservation, Journey, Passager, Client
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



#Gestion du client

class ClientForm(ModelForm):
    """
    A form to allow a client to verify its informations

    Args (See Client and User models):
        first_name
        last_name
        email
        address
    """
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'address': forms.TextInput() 
        }

# User management
class SignUpForm(UserCreationForm):
    """
    A form to create a new client

    Fields (see Client and User models):
    username
        first_name
        last_name
        email
        password1 : Password of the user
        password2 : Password typed again for verification
    """
    first_name = forms.CharField(max_length=30, required=True, help_text='Requis.', label='Prénom')
    last_name = forms.CharField(max_length=30, required=True, help_text='Requis.', label='Nom')
    email = forms.EmailField(required=True, help_text='Requis', label='E-mail')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nom d’utilisateur',
            'password1': 'Mot de passe',
            'password2': 'Confirmation du mot de passe',
        }

class UserUpdateForm(forms.ModelForm):
    """
    A form to update user information

    Fields (see Client and User models):
        first_name
        last_name
        email
    """
    first_name = forms.CharField(max_length=30, required=False, label='Prénom')
    last_name = forms.CharField(max_length=30, required=False, label='Nom')
    email = forms.EmailField(required=True, label='E-mail')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# Reservation and journey management
class JourneySearchForm(forms.Form):
    """
    A form to search for a specific journey using a departure or arrival station

    Fields:
        station (Station): The desired departure/arrival station
        choice (depart/arrivee): A choice to specify if the station is a departure or an arrival station for the query
    """
    station = forms.ModelChoiceField(queryset=Station.objects.all(), required=False, label="Choisir une gare")
    choice = forms.ChoiceField(choices=(('depart', 'Départ'), ('arrivee', 'Arrivée')), required=False, label="Type de trajet")

class ReservationForm(forms.ModelForm):
    """
    A form to create a new reservation

    Fields:
        passengers (Passenger): The passengers to assign to the reservation
        journeys (see Reservation model)
    """
    passengers = forms.ModelMultipleChoiceField(
        queryset=Passager.objects.none(),  # Make sure this queryset is properly set up in the __init__ method.
        label="Sélectionner des passagers pré-enregistrés",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Reservation
        fields = ['journeys'] 
        widgets = {
            'journeys': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['passengers'].queryset = Passager.objects.filter(user=user)
            # Ensure that 'journeys' queryset is also set if needed
            self.fields['journeys'].queryset = Journey.objects.all()  # Adjust as necessary for your business logic


class PassagerForm(forms.ModelForm):
    """
    A form to create or edit a passenger linked to a client

    Fields (see Passenger model):
        first_name
        last_name
        date_of_birth
    """
    class Meta:
        model = Passager
        fields = ['first_name', 'last_name', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }