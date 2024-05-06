from django import forms
from .models import Station, Reservation, Journey, Passager, Client
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



#Gestion du client

class ClientForm(ModelForm):
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

class JourneySearchForm(forms.Form):
    station = forms.ModelChoiceField(queryset=Station.objects.all(), required=False, label="Choisir une gare")
    choice = forms.ChoiceField(choices=(('depart', 'Départ'), ('arrivee', 'Arrivée')), required=False, label="Type de trajet")

#Gestion de la réservation

class ReservationForm(forms.ModelForm):
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