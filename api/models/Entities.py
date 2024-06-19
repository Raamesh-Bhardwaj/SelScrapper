from django.db import models


class EntitiesMaster(models.Model):
    artist_name = models.CharField(max_length=100)
    artist_role = models.CharField(max_length=100)
    program_name = models.CharField(max_length=100)
    Date = models.DateField(blank=True, null=True)
    Time = models.TimeField(blank=True, null=True)
    auditorium = models.CharField(max_length=100)

    def __str__(self):
        return self.artist_name

