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
    artists = ArtistSerializer(many=True)
    programs = ProgramsSerializer(many=True)

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
        # depth = 1
    # def get_artists(self, obj):
    #     artists_arr = []
    #     artists_ids = obj.artists
    #     print(artists_ids)
    #     for artist in artists_ids:
    #         artists_arr.append({"name": artist.name, "role": artist.role})
    #     return artists_arr
    #
    # def get_programs(self, obj):
    #     programs_arr = []
    #     programs_ids = obj.programs
    #     for programs in programs_ids:
    #         programs_arr.append({"name": programs.name, "artists": programs.artists})
    #     return programs_arr
    def validate(self, attrs):
        print(

        )
        return attrs



