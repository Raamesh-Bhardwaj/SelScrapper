from langchain.chains.llm import LLMChain
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
from langchain.prompts import PromptTemplate
# from langchain.chains import SimpleChain
from django.conf import settings
# from api.utils.langchain import  generate_answer1, generate_answer2
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from api.utils import Artist


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

    @staticmethod
    def get_artist(text: str):
        OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', '')
        parser = JsonOutputParser(pydantic_object=Artist)
        model = ChatOpenAI(temperature=0, model="gpt-4-turbo", api_key=f"{OPENAI_API_KEY}")
        prompt = PromptTemplate(
            input_variables=["text", "question1"],
            template="""
                You are a AI agent who answers questions based on text. There should be no verbal explanations and 
                answers should be in one or two words. If you do not know the answer to the question, 
                you should respond with "I don't know". If you know the answer to the question, then the output should 
                in the following format.
                The output should be in the following format:
                {format_instructions}
                
                Based on the following text:
                {text}
                
                Answer the following question:
                {question1}
            """,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        open_chain = prompt | model | parser
        artist_json = open_chain.invoke(
                {
                    "text": text,
                    "question1": "What are the names and corresponding instrument of the artists?"
                }
            )
        return artist_json

    @action(detail=False, methods=['GET'])
    def save_entity(self, request):
        url = self.request.query_params.get("url")
        validator = URLValidator()
        try:
            validator(url)
            raw_text = self.parse_url(url)
            artists_json = self.get_artist(text=raw_text)
            return Response(data={'text': raw_text}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response("Invalid URL", status=status.HTTP_400_BAD_REQUEST)

