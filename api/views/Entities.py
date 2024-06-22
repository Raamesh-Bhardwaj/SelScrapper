from typing import Dict

from langchain.chains.llm import LLMChain
from rest_framework.response import Response
from typing_extensions import Union, List

from api.models import Entities, Artists, Programs, EntitiesMaster
from api.serializers import EntitiesSerializer, ArtistSerializer, ProgramsSerializer
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
from rest_framework.serializers import ValidationError as DRFValidationError
from langchain.prompts import PromptTemplate
# from langchain.chains import SimpleChain
from django.conf import settings
# from api.utils.langchain import  generate_answer1, generate_answer2
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from api.utils import Artist, Program, DateAndTime, template
from django.forms.models import model_to_dict


OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', '')


class EntitiesViewSet(viewsets.ModelViewSet):
    serializer_class = EntitiesSerializer
    permission_classes = [AllowAny]
    artists_serializer = ArtistSerializer
    program_serializer = ProgramsSerializer

    def get_queryset(self):
        return EntitiesMaster.objects.all()

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

    def get_artists(self, text: str):
        parser = JsonOutputParser(pydantic_object=Artist)
        model = ChatOpenAI(temperature=0, model="gpt-4-turbo", api_key=f"{OPENAI_API_KEY}")
        prompt = PromptTemplate(
            input_variables=["text", "question1"],
            template=template,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        open_chain = prompt | model | parser
        artist_json = open_chain.invoke(
                {
                    "text": text,
                    "question1": "What are the names and corresponding instrument of the artists?"
                }
            )
        artist_json = self.process_gpt_response(artist_json, params=["name", "role"])
        self.save_artists(artist_json)
        return artist_json

    @staticmethod
    def process_gpt_response(response, **kwargs) -> List[Dict]:
        if type(response) is list:
            return response
        elif type(response) is dict:
            json_list = []
            if 'params' in kwargs:
                params_arr = kwargs.get('params')
                first_param = params_arr[0]
                second_param = params_arr[1]
                r_1 = response.get(first_param)
                r_2 = response.get(second_param)
                for i in range(len(r_1)):
                    json_list.append({first_param: r_1[i], second_param: r_2[i]})
            return json_list

    def save_artists(self, artist_json):
        serializer_data = []
        for artist_dict in artist_json:
            serializer = self.artists_serializer(data=artist_dict)
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                serializer_data.append(serializer.data)
            except DRFValidationError:
                qs = Artists.objects.filter(name=artist_dict.get('name'), role=artist_dict.get('role'))
                serializer = self.artists_serializer(qs, many=True)
                serializer_data.append(serializer.data[0])
        return serializer_data

    def get_programs(self, text: str):
        parser = JsonOutputParser(pydantic_object=Program)
        model = ChatOpenAI(temperature=0, model="gpt-4-turbo", api_key=f"{OPENAI_API_KEY}")
        prompt = PromptTemplate(
            input_variables=["text", "question1"],
            template=template,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        open_chain = prompt | model | parser
        programs_json = open_chain.invoke(
            {
                "text": text,
                "question1": "What are the names and corresponding artists of the program?"
            }
        )
        programs_json['artists'] = programs_json.pop('artist')
        programs_json = self.process_gpt_response(programs_json, params=["name", "artists"])
        programs_json = self.save_programs(programs_json)
        return programs_json

    def save_programs(self, programs_json):
        programs_data = []
        for prg_dict in programs_json:
            serializer = self.program_serializer(data=prg_dict)
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                json_dict = serializer.data
                json_dict.pop('id')
                programs_data.append(serializer.data)
            except DRFValidationError:
                qs = Programs.objects.filter(name=prg_dict.get('name'), artists=prg_dict.get('artists'))
                serializer = self.program_serializer(qs, many=True)
                json_dict = serializer.data[0]
                json_dict.pop('id')
                programs_data.append(json_dict)
        return programs_data

    @staticmethod
    def get_auditorium(text: str):
        model = ChatOpenAI(temperature=0, model="gpt-4-turbo", api_key=f"{OPENAI_API_KEY}")
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
        open_chain = prompt | model
        venue = open_chain.invoke(
            {
                "text": text,
                "question1": "Where is the venue of the performance?"
            }
        )
        return venue.content

    @staticmethod
    def get_date_and_time(text: str):
        parser = JsonOutputParser(pydantic_object=DateAndTime)
        model = ChatOpenAI(temperature=0, model="gpt-4-turbo", api_key=f"{OPENAI_API_KEY}")
        prompt = PromptTemplate(
            input_variables=["text", "question1"],
            template=template,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        open_chain = prompt | model | parser
        artist_json = open_chain.invoke(
            {
                "text": text,
                "question1": "What is the date and time of the performances?"
            }
        )
        return artist_json.get('date'), artist_json.get('time')

    @action(detail=False, methods=['GET'])
    def save_entity(self, request):
        url = self.request.query_params.get("url")
        validator = URLValidator()
        try:
            validator(url)
            raw_text = self.parse_url(url)
            artists_json = self.get_artists(text=raw_text)
            programs_json = self.get_programs(text=raw_text)
            venue = self.get_auditorium(text=raw_text)
            date, time = self.get_date_and_time(text=raw_text)
            self.save_entities(url, artists_json, programs_json, venue, date, time)
            return Response(data={'artists': artists_json, 'programs': programs_json, "venue": venue,
                                  "date": date, "time": time}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response("Invalid URL", status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_artists_ids(artists_json):
        artists_ids = []
        for artist in artists_json:
            name = artist.get('name')
            role = artist.get('role')
            artists = Artists.objects.filter(name=name, role=role).first()
            artists_ids.append(artists.id)
        return artists_ids

    @staticmethod
    def get_programs_ids(programs_json):
        programs_ids = []
        for program in programs_json:
            name = program.get('name')
            artists = program.get('artists')
            programs = Programs.objects.filter(name=name, artists=artists).first()
            programs_ids.append(programs.id)
        return programs_ids


    def save_entities(self,url, artistes_json, programs_json, venue, date, time):
        entities = EntitiesMaster.objects.filter(url=url)
        artists_id = self.get_artists_ids(artistes_json)
        programs_id = self.get_programs_ids(programs_json)
        if entities.exists():
            entities_qs = entities.first()
            entities_serializer = self.get_serializer(data=entities_qs)
            entities_serializer.artists.set(artists_id)
            entities_serializer.programs.set(programs_id)
        else:
            serializer = self.serializer_class(data={"url": url, "auditorium": venue, "date": date, "time": time,
                                                     "artists": artists_id, "programs": programs_id})
            serializer.is_valid(raise_exception=True)
            serializer.save()

    @action(detail=False, methods=['GET'])
    def get_entity(self, request):
        url = self.request.query_params.get("url")
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            return Response("Invalid URL", status=status.HTTP_400_BAD_REQUEST)
        else:
            entities = EntitiesMaster.objects.filter(url=url)
            if entities.exists():
                qs = model_to_dict(EntitiesMaster.objects.filter(url=url).first())
                qs.pop('id')
                qs = self.process_entity_serialization(qs)
                return Response(qs, status=status.HTTP_200_OK)
            else:
                return Response("URL Not Found", status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def process_entity_serialization(qs):
        artists = qs.pop('artists')
        artists_arr = []
        for artist in artists:
            artists_arr.append({"name": artist.name, "role": artist.role})
        qs['artists'] = artists_arr
        programs = qs.pop('programs')
        programs_arr = []
        for program in programs:
            programs_arr.append({"name": program.name, "artists": program.artists})
        qs['programs'] = programs_arr
        return qs
