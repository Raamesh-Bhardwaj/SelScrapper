from django.db import models

from api.utils import Artist, Program


class EntitiesMaster(models.Model):
    url = models.URLField(blank=False, null=False)
    artists = models.ManyToManyField("Artists")
    programs = models.ManyToManyField("Programs")
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    auditorium = models.CharField(max_length=100)

    def __str__(self):
        return self.artists.name


class Artists(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Programs(models.Model):
    name = models.CharField(max_length=100)
    artists = models.ForeignKey(Artists, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
