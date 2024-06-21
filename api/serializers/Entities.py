from rest_framework import serializers

from api.models import Entities, Artists
from api.utils import Artist


class EntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entities
        fields = '__all__'


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artists
        fields = '__all__'
        depth = 1