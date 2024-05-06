from django import forms
from .models import Gare, Reservation, Journey, Passager, Client
from django.forms import ModelForm, inlineformset_factory, DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import datetime

#Gestion du client

class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'address': forms.TextInput() 
        }

#Gestion de l'utilisateur
        
class SignUpForm(UserCreationForm):
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
    first_name = forms.CharField(max_length=30, required=False, label='Prénom')
    last_name = forms.CharField(max_length=30, required=False, label='Nom')
    email = forms.EmailField(required=True, label='E-mail')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


#Gestion de la recherche trajet

class TrajetSearchForm(forms.Form):
    station = forms.ModelChoiceField(queryset=Gare.objects.all(), required=False, label="Choisir une gare")
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


from django import forms
from .models import Reservation, Passager
# Adding the DateTimeField for departure date and time
#Gestion de la réservation

class ReservationForm(forms.ModelForm):
    passengers = forms.ModelMultipleChoiceField(
        queryset=Passager.objects.none(),
        widget=forms.CheckboxSelectMultiple,
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


#Formulaire passager

class PassagerForm(forms.ModelForm):
    class Meta:
        model = Passager
        fields = ['first_name', 'last_name', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }