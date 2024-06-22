from django.db import models

from api.utils import Artist, Program


class EntitiesMaster(models.Model):
    url = models.URLField(blank=False, null=False, unique=True)
    artists = models.ManyToManyField("Artists")
    programs = models.ManyToManyField("Programs")
    date = models.CharField(max_length=100, blank=False, null=False, default=None)
    time = models.CharField(max_length=50, blank=True, null=True, default=None)
    auditorium = models.CharField(max_length=100)

    def __str__(self):
        return self.artists.name


class Artists(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ["name", "role"]

    def __str__(self):
        return self.name


class Programs(models.Model):
    name = models.CharField(max_length=100)
    artists = models.CharField(max_length=100)

    class Meta:
        unique_together = ["name", "artists"]

    def __str__(self):
        return self.name
