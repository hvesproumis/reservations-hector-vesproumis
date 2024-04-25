from django import forms
from .models import Gare, Reservation, Trajet, Passager, Client
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.models import User


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'address']  # Include all fields you need
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'address': forms.TextInput() 
        }


class TrajetSearchForm(forms.Form):
    gare = forms.ModelChoiceField(queryset=Gare.objects.all(), required=False, label="Choisir une gare")
    choix = forms.ChoiceField(choices=(('depart', 'Départ'), ('arrivee', 'Arrivée')), required=False, label="Type de trajet")

from django import forms
from .models import Reservation, Passager

class ReservationForm(forms.ModelForm):
    existing_passager = forms.ModelChoiceField(
        queryset=Passager.objects.none(), label="Sélectionner un passager pré-enregistré",
        empty_label="Sélectionnez", widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Reservation
        fields = ['trajet', 'existing_passager', 'seat_number', 'car_number']
        widgets = {
            'trajet': forms.Select(attrs={'class': 'form-control'}),
            'seat_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_number': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['existing_passager'].queryset = Passager.objects.filter(user=user)

class PassagerForm(forms.ModelForm):
    class Meta:
        model = Passager
        fields = ['first_name', 'last_name', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }