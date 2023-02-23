import openai
import json

import os
import environ
import re
import pandas as pd

from pathlib import Path

import requests

from django.utils.translation import gettext_lazy

from datetime import datetime

from .models import ProductReviews, ReviewsAnalyzed, ProductDetails

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR,  ".env"))

OPEN_AI_KEY = env('OPEN_AI_KEY', default='')

os.environ['OPENAI_API_KEY'] = OPEN_AI_KEY

# get amazon reviews
def get_reviews(asin, pg_num):
    url = "https://amazon23.p.rapidapi.com/reviews"
    
    querystring = {
        "asin": asin,
        "sort_by": "recent",
        "country":"US", 
        "page": pg_num}

    headers = {
        "X-RapidAPI-Key": env('RAPID_API_KEY', default=''),
        "X-RapidAPI-Host": "amazon23.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

def get_single_product_detail(asin):
    url = "https://amazon23.p.rapidapi.com/product-details"

    querystring = {
        "asin": asin, 
        "country": "US"
        }

    headers = {
        "X-RapidAPI-Key": env('RAPID_API_KEY', default=''),
        "X-RapidAPI-Host": "amazon23.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

def save_reviews(user, asin, pg_num, response):
    doc = ProductReviews(
        USER = user,
        ASIN = asin,
        COUNTRY = 'US',
        SORT_BY = 'recent',
        PAGE_NUM = pg_num,
        QUERY_DATE = datetime.now(),
        RESPONSE = response
    )
    doc.save()

def save_product_detail(user, asin, response):
    doc = ProductDetails(
        USER = user,
        ASIN = asin,
        COUNTRY = 'US',
        RESPONSE = response,
        QUERY_DATE = datetime.now()
    )
    doc.save()
    

def read_json_file(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data

# Set the API key
openai.api_key = OPEN_AI_KEY

# Define the prompts

def open_ai_summarize_text(prompt, engine, max_tokens):
    response = openai.Completion.create(
        # engine="ada",
        # engine="text-davinci-002",
        # engine="babbage",
        # engine="curie",
        engine=engine,
        prompt=prompt,
        max_tokens=max_tokens,
        n = 3,
        stop=None,
        # temperature=0.5,
        temperature=0.5,
    )

    return response

def agg_reviews_for_gpt(user, asin):
    all_reviews = []

    data_list = ProductReviews.objects.filter(USER=user, ASIN=asin).values('RESPONSE').distinct()
    data_list = [json.loads(x['RESPONSE']) for x in data_list]

    for ten_ct in data_list:
        try:
            for x in ten_ct['result']:
                all_reviews.append(x['review'])
        except:
            pass
        
    review_chunks = []

    all_str = ''

    for x in all_reviews:
        if len(all_str + x) < 2000:
            all_str += ';'
            all_str += x
        else:
            review_chunks.append(all_str)
            all_str = ''

    review_chunks.append(all_str)

    return review_chunks[0]

def gpt_analyze_reviews(agg_reviews, asin, partial_prompt):
    prompt = '{}"{}"'.format(partial_prompt, agg_reviews)
    x = open_ai_summarize_text(prompt, engine='text-davinci-003', max_tokens=500)
    # x = open_ai_summarize_text(prompt, engine='text-curie-001', max_tokens=400)

    x = json.loads(json.dumps(x))

    results = re.sub('\n', '', str(x['choices'][0]['text']))
    completion_tokens = str(x['usage']['completion_tokens'])
    prompt_tokens = str(x['usage']['prompt_tokens'])

    output = {
            "asin": asin,
            "prompt": partial_prompt,
            "gpt_evaluation": results,
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
        }

    return output

def save_gpt_results(user, asin, partial_prompt, gpt_data):
    doc = ReviewsAnalyzed(
        USER = user,
        ASIN = asin,
        PROMPT = partial_prompt,
        QUERY = '',
        GPT_RESPONSE = gpt_data['gpt_evaluation'],
        COMPLETION_TOKENS = gpt_data['completion_tokens'],
        PROMPT_TOKENS = gpt_data['prompt_tokens'],
        QUERY_DATE = datetime.now(),
    )
    doc.save()

def asin_gpt_data(user, asin, prompts):
    retrived_asin_data = list(ReviewsAnalyzed.objects.filter(USER=user, ASIN=asin).all().distinct().values())

    product_details = list(ProductDetails.objects.filter(USER=user, ASIN=asin).all().distinct().values())[0]
    product_details = json.loads(product_details['RESPONSE'])
    product_details = product_details['result'][0]
    try:
        product_img = product_details["variants"][0]["images"][0]["large"]
    except:
        product_img = ''
    # print(json.dumps(product_details, indent=4))

    disliked_reviews = [x['GPT_RESPONSE'] for x in retrived_asin_data if x['PROMPT'] == prompts['dislike_partial_prompt']][0]
    disliked_reviews = re.sub('-|:|[0-9]\\.', ';' , disliked_reviews)
    disliked_reviews = disliked_reviews.split(';')
    disliked_reviews = list(set(disliked_reviews))

    liked_reviews = [x['GPT_RESPONSE'] for x in retrived_asin_data if x['PROMPT'] == prompts['like_partial_prompt']][0]
    liked_reviews = re.sub('-|:|[0-9]\\.', ';' , liked_reviews)
    liked_reviews = liked_reviews.split(';')
    liked_reviews = list(set(liked_reviews))

    description_reviews = [x['GPT_RESPONSE'] for x in retrived_asin_data if x['PROMPT'] == prompts['description_partial_prompt']][0]
    description_reviews = re.sub('-|:|[0-9]\\.', ';' , description_reviews)
    description_reviews = description_reviews.split(';')
    description_reviews = list(set(description_reviews))

    return {
        'asin': asin,
        'product_details': product_details,
        'product_img': product_img,
        'liked_reviews': liked_reviews,
        'disliked_reviews': disliked_reviews,
        'description_reviews': description_reviews,
    }