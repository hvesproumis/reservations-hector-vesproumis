"""
This file contains custom forms used in the different views
"""

from django import forms
from .models import Station, Reservation, Journey, Passager, Client
from django.forms import ModelForm, inlineformset_factory, DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import datetime


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
    first_name = forms.CharField(
        max_length=100,
        required=False,
        label='Prénom',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=False,
        label='Nom',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    email = forms.EmailField(
        required=False,
        label='Email',
        widget=forms.EmailInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'address']
        widgets = {
            'address': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        # Initialisez les champs first_name, last_name, et email avec les valeurs de l'utilisateur lié
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

        
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
    choice = forms.ChoiceField(choices=(('depart', 'Départ'), ('arrivee', 'Arrivée'), ('dep_and_arrival', 'Départ et Arrivée')), required=False, label="Type de trajet")
    
    # Adding the DateTimeField for departure date and time
    depart_date_time = forms.DateTimeField(
        required=False,
        label="Choisir la date et l'heure de départ",
        widget=DateTimeInput(
            format='%Y-%m-%d %H:%M',  # Format for the date and time input
            attrs={'type': 'datetime-local'}  # Ensures HTML5 date-time picker
        )
    )

    def clean_depart_date_time(self):
        # Get the departure date/time from the form -> checked with isvalid method
        depart_date_time = self.cleaned_data.get('depart_date_time')
        
        if depart_date_time and depart_date_time < datetime.now():
            # If it's earlier than the current time, raise a validation error
            raise ValidationError("La date et l'heure de départ ne peuvent pas être dans le passé.")
        
        
        return depart_date_time


# Adding the DateTimeField for departure date and time
#Gestion de la réservation

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
        widget=forms.CheckboxSelectMultiple()
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