from rest_framework import serializers

from api.models import Artists, Programs, EntitiesMaster
from api.utils import Artist

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artists
        fields = '__all__'
        depth = 1

    def validate(self, attrs):
        # Validate unique_together constraint
        name = attrs.get('name')
        role = attrs.get('role')

        if Artists.objects.filter(name=name, role=role).exists():
            raise serializers.ValidationError('The combination of name and role already exists')

        return attrs


class ProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = '__all__'
        depth = 1

    def validate(self, attrs):
        # Validate unique_together constraint
        name = attrs.get('name')
        artists = attrs.get('artists')

        if Programs.objects.filter(name=name, artists=artists).exists():
            raise serializers.ValidationError('The combination of name and artist already exists')

        return attrs


class EntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntitiesMaster
        fields = [
            "id",
            "url",
            "artists",
            "programs",
            "date",
            "time",
            "auditorium",
        ]
        depth = 1




