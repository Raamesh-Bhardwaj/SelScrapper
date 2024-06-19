from api.models import Entities
from api.serializers import EntitiesSerializer
from rest_framework import status, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny


class EntitiesViewSet(viewsets.ModelViewSet):
    serializer_class = EntitiesSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Entities.objects.all()