import docx
import openai
import json

import os
import environ
import re
import pandas as pd

from pathlib import Path

from django.utils.translation import gettext_lazy


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR,  ".env"))

OPEN_AI_KEY = env('OPEN_AI_KEY', default='')

os.environ['OPENAI_API_KEY'] = OPEN_AI_KEY

def read_word_doc(file_path):
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return ' '.join(fullText)

# Set the API key
openai.api_key = OPEN_AI_KEY

# Define the prompt


# Send the prompt to the Ada model
def open_ai_summarize_text(prompt, engine, max_tokens):
    response = openai.Completion.create(
        # engine="ada",
        # engine="text-davinci-002",
        # engine="babbage",
        # engine="curie",
        engine=engine,
        prompt=prompt,
        max_tokens=max_tokens,
        n = 1,
        stop=None,
        temperature=0.5,
    )

    return response

def interpret_text(query, doc_text):
    prompt = 'read the following text and tell me "{}": {}'.format(query, doc_text)
    # engine="ada",
    # engine="text-davinci-002",
    # engine="babbage",
    # engine="curie",
    x = open_ai_summarize_text(prompt, engine='text-davinci-002', max_tokens=2290)
    # x = open_ai_summarize_text(prompt, engine='ada', max_tokens=1000)

    x = json.loads(json.dumps(x))

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(x)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    

    gpt_response = re.sub('\n', '', str(x['choices'][0]['text']))
    completion_tokens = str(x['usage']['completion_tokens'])
    prompt_tokens = str(x['usage']['prompt_tokens'])

    output = {
            "query": query,
            "doc_text": doc_text,
            "gpt_response": gpt_response,
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
        }

    # output = pd.DataFrame([output])

    return output