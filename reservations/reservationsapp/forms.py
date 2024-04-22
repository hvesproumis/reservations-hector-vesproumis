from django import forms
from .models import Gare

class TrajetSearchForm(forms.Form):
    gare = forms.ModelChoiceField(queryset=Gare.objects.all(), required=False, label="Choisir une gare")
    choix = forms.ChoiceField(choices=(('depart', 'Départ'), ('arrivee', 'Arrivée')), required=False, label="Type de trajet")
