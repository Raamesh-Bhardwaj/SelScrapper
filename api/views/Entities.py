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
# from langchain import LangChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
# from langchain.chains import SimpleChain
from django.conf import settings
# from api.utils.langchain import  generate_answer1, generate_answer2


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
    def feed_llm(text: str):
        OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', '')
        llm = OpenAI(api_key=OPENAI_API_KEY)
        prompt = PromptTemplate(
            input_variables=["text", "question1"],
            template="""
                You are a AI agent who answers questions based on text. There should be no verbal explanations and 
                answers should be in one or two words. If you do not know the answer to the question, 
                you should respond with "I don't know".
                
                Based on the following text:
                {text}
                
                Answer the following question:
                {question1}
            """
        )
        open_chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
        print(open_chain.run(text=text, question1="What are the name of the artists?"))

    @action(detail=False, methods=['GET'])
    def save_entity(self, request):
        url = self.request.query_params.get("url")
        validator = URLValidator()
        try:
            validator(url)
            raw_text = self.parse_url(url)
            self.feed_llm(text=raw_text)
            return Response(data={'text': raw_text}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response("Invalid URL", status=status.HTTP_400_BAD_REQUEST)

