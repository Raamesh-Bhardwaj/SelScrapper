from rest_framework.response import Response

from api.models import Entities
from api.serializers import EntitiesSerializer
from rest_framework import status, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class EntitiesViewSet(viewsets.ModelViewSet):
    serializer_class = EntitiesSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Entities.objects.all()

    @staticmethod
    def validate_url(url):
        validator = URLValidator()
        try:
            validator(url)
            return True
        except ValidationError:
            return False

    @staticmethod
    def parse_url(url, div_id='buy'):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, div_id))
        )
        element_text = element.text
        driver.quit()

        return element_text

    @action(detail=False, methods=['GET'])
    def save_entity(self, request):
        url = self.request.query_params.get("url")
        validator = URLValidator()
        try:
            validator(url)
            raw_text = self.parse_url(url)
        except ValidationError:
            return Response("Invalid URL", status=status.HTTP_400_BAD_REQUEST)

