from django.db import models


class EntitiesMaster(models.Model):
    url = models.URLField(blank=False, null=False)
    artist_name = models.CharField(max_length=100)
    artist_role = models.CharField(max_length=100)
    program_name = models.CharField(max_length=100)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    auditorium = models.CharField(max_length=100)

    def __str__(self):
        return self.artist_name

