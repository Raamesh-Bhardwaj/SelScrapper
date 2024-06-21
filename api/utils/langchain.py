from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Prompt template for the first question
template1 = """
{system_prompt}

Based on the following text:
{text}

Answer the following question:
{question1}
"""

prompt_template1 = PromptTemplate(
    input_variables=["system_prompt", "text", "question1"],
    template=template1,
)

# Prompt template for the second question, which uses the answer from the first question
template2 = """
Using the information provided in the answer:
{answer1}

Answer the following question:
{question2}
"""

prompt_template2 = PromptTemplate(
    input_variables=["answer1", "question2"],
    template=template2
)


def generate_answer1(question, context):
    formatted_prompt = prompt_template1.format(text=context, question1=question)
    return formatted_prompt


def generate_answer2(answer1, question):
    formatted_prompt = prompt_template2.format(answer1=answer1, question2=question)
    return formatted_prompt


class Artist(BaseModel):
    name: str = Field(description="name of artist")
    role: str = Field(description="name of instrument")


class Program(BaseModel):
    name: str = Field(description="name of program")
    artist: str = Field(description="name of artist")


class DateAndTime(BaseModel):
    date: str = Field(description="date of performance")
    time: str = Field(description="time of performance")


template = """
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
"""
