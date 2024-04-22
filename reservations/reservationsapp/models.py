from django.db import models

class Gare(models.Model):
    ville = models.CharField(max_length=200)
    nomgare = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.ville} {self.nomgare}"

    
class Trajet(models.Model):
    depgare = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='depart_trajets', db_comment="Gare de départ")
    arrgare = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='arrivee_trajets', db_comment="Gare d'arrivée")
    depdh = models.DateTimeField(db_comment="Date et heure de départ",)
    arrdh = models.DateTimeField(db_comment="Date et heure d'arrivée",)
    def __str__(self):
        return f"Trajet de {self.depgare} à {self.arrgare} le {self.depdh.strftime('%Y-%m-%d %H:%M')} - Arrivée le {self.arrdh.strftime('%Y-%m-%d %H:%M')}"

