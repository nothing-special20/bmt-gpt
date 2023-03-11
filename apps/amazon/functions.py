import openai
import json

import os
import environ
import re
import pandas as pd

from pathlib import Path

import requests
import math

from django.utils.translation import gettext_lazy
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from datetime import datetime

from .models import ProductReviews, ReviewsAnalyzed, ProductDetails, ProcessedProductReviews, ReviewsAnalyzedInternalModels

from collections import Counter

from .functions_dashboard import bar_chart

from asgiref.sync import sync_to_async

import time

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR,  ".env"))

OPEN_AI_KEY = env('OPEN_AI_KEY', default='')

os.environ['OPENAI_API_KEY'] = OPEN_AI_KEY

# like_partial_prompt = "From the following reviews, Write the Top 10 things people like about the product, each review is separated by a semicolon: "
# dislike_partial_prompt = "From the following reviews, Write the Top 10 things people dislike about the product, each review is separated by a semicolon: "
# description_partial_prompt = "From the following reviews, Write the Top 10 phrases people used to describe the product, each review is separated by a semicolon: "
like_partial_prompt = "From the following reviews, create 10 categories descrbing what people like about the product and list the number of reviews that fit into said bucket, each review is separated by a semicolon: "
dislike_partial_prompt = "From the following reviews, create 10 categories descrbing what people dislike about the product and list the number of reviews that fit into said bucket, each review is separated by a semicolon: "
description_partial_prompt = "From the following reviews, create 10 categories descrbing what phrases people use to describe and list the number of reviews that fit into said bucket, each review is separated by a semicolon:  "

prompts = {
    'dislike_partial_prompt': dislike_partial_prompt,
    'like_partial_prompt': like_partial_prompt,
    'description_partial_prompt': description_partial_prompt,
}

# get amazon reviews
def _get_reviews(asin, pg_num):
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

def get_reviews(asin, pg_num):
    # '{"errors":[{"param":"","msg":"Not expected text found"}]}'
    counter = 0
    while counter < 5:
        response = _get_reviews(asin, pg_num)
        _response = json.loads(response)
        if 'errors' in _response.keys():
            time.sleep(5)
            _response = json.loads("{}")
            counter += 1
        else:
            break

    return response

def _get_single_product_detail(asin):
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

def get_single_product_detail(asin):
    counter = 0
    while counter < 5:
        try:
            response = _get_single_product_detail(asin)
            _response = json.loads(response)
            product_details = _response['result'][0]
            break
        except:
            counter += 1
            time.sleep(5)
            product_details = json.loads({})

    return product_details

def get_keyword_details(keyword):
    url = 'https://amazon23.p.rapidapi.com/product-search'

    querystring = {
        "query": keyword, 
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

def process_reviews(user, raw_reviews):
    _reviews = json.loads(raw_reviews)
    output = []
    try:
        reviews = _reviews['result']
        for rev in reviews:
            doc = ProcessedProductReviews(
                USER = user,
                REVIEW_ID = rev['id'],
                ASIN_ORIGINAL_ID = rev['asin']['original'],
                ASIN_VARIANT_ID = rev['asin']['variant'],
                REVIEWER_NAME = rev['name'],
                RATING = rev['rating'],
                REVIEW_DATE = rev['date']['date'],
                REVIEW_DATE_UNIX = rev['date']['unix'],
                TITLE = rev['title'],
                REVIEW = rev['review'],
                VERIFIED_PURCHASE = rev['verified_purchase'],
                LOAD_DATE = datetime.now(),
            )

            doc.save()
            data = serializers.serialize('python', [doc])[0]

            # Convert the dict to a JSON string with custom encoding
            _json_data = json.dumps(data, cls=DjangoJSONEncoder)
            json_data = json.loads(_json_data)['fields']
            output.append(json_data)
    except:
        print(_reviews)
        print(_reviews.keys())

    return output

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

def open_ai_summarize_text(prompt, max_tokens):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        n = 1,
        stop=None,
        temperature=0.5,
    )

    return response


def asin_review_list(user, asin, review_rating):
    all_reviews = []

    data_list = ProductReviews.objects.filter(USER=user, ASIN=asin).values('RESPONSE').distinct()
    data_list = [json.loads(x['RESPONSE']) for x in data_list]

    for ten_ct in data_list:
        try:
            for x in ten_ct['result']:
                if x['verified_purchase'] == True and (review_rating is None or x['rating'] in review_rating):
                    all_reviews.append(x['review'])
        except:
            pass

    return all_reviews

def split_list_into_chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]

def asin_review_list_resample(user, asin_list, review_rating):
    raw_reviews = []
    max_reviews = 0
    chunk_size = 20
    for asin in asin_list:
        single_asin_reviews = asin_review_list(user, asin, review_rating)
        max_reviews = max(max_reviews, len(single_asin_reviews))
        #split reviews into chunks of N
        single_asin_reviews_chunks = split_list_into_chunks(single_asin_reviews, chunk_size)
        raw_reviews.append(single_asin_reviews_chunks)

    resample_reviews = []

    for index in range(math.ceil(max_reviews / chunk_size)):
        for asin_reviews in raw_reviews:
            try:
                resample_reviews.extend(asin_reviews[index])
            except:
                pass

    return resample_reviews

def agg_reviews_for_gpt(user, asin_list, review_rating=None):
    all_reviews = asin_review_list_resample(user, asin_list, review_rating)
        
    review_chunks = []

    all_str = ''

    for x in all_reviews:
        if len(all_str + x) < 4000:
            all_str += ';'
            all_str += x
        else:
            review_chunks.append(all_str)
            all_str = ''

    review_chunks.append(all_str)

    return review_chunks[0]

def gpt_analyze_reviews(agg_reviews, asin, partial_prompt):
    asin = ';'.join(asin)
    prompt = '{}"{}"'.format(partial_prompt, agg_reviews)
    x = open_ai_summarize_text(prompt, max_tokens=1500)

    x = json.loads(json.dumps(x))

    results = str(x['choices'][0]['message']['content'])
    results = re.sub('\n', '', results)
    completion_tokens = str(x['usage']['completion_tokens'])
    prompt_tokens = str(x['usage']['prompt_tokens'])

    output = {
            "asin": asin,
            "prompt": partial_prompt,
            "gpt_evaluation": results,
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
        }

    print('gpt analysis done')

    return output

def save_gpt_results(user, asin, partial_prompt, gpt_data):
    asin = ';'.join(asin)
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

def extract_review_count(text):
    try:
        output = int(re.findall('[0-9]{1,3}', re.findall('[0-9]{1,3} review', text)[0])[0])
    except:
        output = 0
    return output

def asin_gpt_data(user, asin, prompts):
    retrived_asin_data = list(ReviewsAnalyzed.objects.filter(USER=user, ASIN=asin).all().distinct().values())

    try:
        product_details = list(ProductDetails.objects.filter(USER=user, ASIN=asin).all().distinct().values())[0]
        product_details = json.loads(product_details['RESPONSE'])
        product_details = product_details['result'][0]

    except:
        product_details = '_'
        
    try:
        product_img = product_details["variants"][0]["images"][0]["large"]
    except:
        product_img = ''
    # print(json.dumps(product_details, indent=4))

    disliked_reviews = [x['GPT_RESPONSE'] for x in retrived_asin_data if x['PROMPT'] == prompts['dislike_partial_prompt']][0]
    # disliked_reviews = re.sub('-|:|[0-9]{1,2}\\.', ';' , disliked_reviews)
    disliked_reviews = re.sub('[0-9]{1,2}\\.', ';' , disliked_reviews)
    disliked_reviews = disliked_reviews.split(';')
    disliked_reviews = list(set(disliked_reviews))
    disliked_reviews_rank = [extract_review_count(x) for x in disliked_reviews]
    disliked_reviews = sorted(disliked_reviews, key=lambda x: extract_review_count(x), reverse=True)
    # disliked_reviews = disliked_reviews[disliked_reviews_rank]

    liked_reviews = [x['GPT_RESPONSE'] for x in retrived_asin_data if x['PROMPT'] == prompts['like_partial_prompt']][0]
    # liked_reviews = re.sub('-|:|[0-9]{1,2}\\.', ';' , liked_reviews)
    liked_reviews = re.sub('[0-9]{1,2}\\.', ';' , liked_reviews)
    liked_reviews = liked_reviews.split(';')
    liked_reviews = list(set(liked_reviews))
    liked_reviews = sorted(liked_reviews, key=lambda x: extract_review_count(x), reverse=True)

    description_reviews = [x['GPT_RESPONSE'] for x in retrived_asin_data if x['PROMPT'] == prompts['description_partial_prompt']][0]
    # description_reviews = re.sub('-|:|[0-9]{1,2}\\.', ';' , description_reviews)
    description_reviews = re.sub('[0-9]{1,2}\\.', ';' , description_reviews)
    description_reviews = description_reviews.split(';')
    description_reviews = list(set(description_reviews))
    description_reviews = sorted(description_reviews, key=lambda x: extract_review_count(x), reverse=True)

    return {
        'asin': asin,
        'product_details': product_details,
        'product_img': product_img,
        'liked_reviews': liked_reviews,
        'disliked_reviews': disliked_reviews,
        'description_reviews': description_reviews,
    }

def store_gpt_results(user, asin, prompts):
    good_reviews = agg_reviews_for_gpt(user, asin, [4, 5])
    bad_reviews = agg_reviews_for_gpt(user, asin, [1, 2])
    all_reviews = agg_reviews_for_gpt(user, asin)

    print('good_reviews', len(good_reviews))
    print('bad_reviews', len(bad_reviews))
    print('all_reviews', len(all_reviews))

    likes = gpt_analyze_reviews(good_reviews, asin, prompts['like_partial_prompt'])

    save_gpt_results(user, asin, prompts['like_partial_prompt'], likes)

    dislikes = gpt_analyze_reviews(bad_reviews, asin, prompts['dislike_partial_prompt'])
    
    save_gpt_results(user, asin, prompts['dislike_partial_prompt'], dislikes)
    
    descriptions = gpt_analyze_reviews(all_reviews, asin, prompts['description_partial_prompt'])

    save_gpt_results(user, asin, prompts['description_partial_prompt'], descriptions)
    
    


def split_list_into_sublists(list_to_split, number_of_sublists):
    length_of_sublist = len(list_to_split) // number_of_sublists
    return [list_to_split[i:i+length_of_sublist] for i in range(0, len(list_to_split), length_of_sublist)]


def rate_limiter(user, asin_limit):
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    all_user_asins = ReviewsAnalyzed.objects.filter(USER=user, QUERY_DATE__year=current_year, QUERY_DATE__month=current_month).values('ASIN').distinct()
    all_user_asins = [x['ASIN'] for x in list(all_user_asins)]

    return len(all_user_asins) < asin_limit

@sync_to_async
def review_analysis_fields(user, asin, word_type, rating_filter=[1,2,3,4,5]):
    fields = ['reviewsanalyzedopenai__' + word_type, 'RATING']
    data = ProcessedProductReviews.objects.filter(USER=user, ASIN_ORIGINAL_ID=asin, RATING__in=rating_filter).all().select_related('PROCESSED_RECORD_ID').distinct().values(*fields)
    data = list(data)

    return data

@sync_to_async
def review_analysis_most_common_words(user, asin, word_type, rating_filter=[1,2,3,4,5]):
    # fields = ['reviewsanalyzedinternalmodels__NOUNS', 'reviewsanalyzedinternalmodels__ADJECTIVES', 'RATING']
    fields = ['reviewsanalyzedopenai__' + word_type, 'RATING']
    data = ProcessedProductReviews.objects.filter(USER=user, ASIN_ORIGINAL_ID=asin, RATING__in=rating_filter).all().select_related('PROCESSED_RECORD_ID').distinct().values(*fields)
    data = list(data)
    # _nouns = [x['reviewsanalyzedinternalmodels__' + word_type] for x in data]
    _nouns = [x['reviewsanalyzedopenai__' + word_type] for x in data]

    nouns = []
    for x in _nouns:
        if x != None and x not in ['NA', 'reviewer'] and len(x) > 0:
            punctuation = '''!()-[]{};:,'"\,<>./?@#$%^&*_~'''
            x = x.replace(punctuation, " ")
            x = x.replace("  ", " ")
            x = x.lower()
            x = x.strip()
            while x[0] == ' ':
                x = x[1:]

            if isinstance(x, list):
                xlist = x

            if ',' in x:
                xlist = x.split(' ')
                xlist = [z.strip() for z in xlist]

            else:
                xlist = [x]
                
            for y in xlist:
                nouns.append(y)

    try:
        most_common_words = Counter(nouns).most_common(15)
        most_common_words = [pd.DataFrame([{'word': x[0], 'count': x[1]}]) for x in most_common_words]
        most_common_words = pd.concat(most_common_words)

    except:
        most_common_words = pd.DataFrame([{'word': '', 'count': ''}])
    
    return most_common_words

async def create_word_bar_chart(user, asin, word_type, positive_ratings, chart_config):
    most_common_nouns_positive = await review_analysis_most_common_words(user, asin, word_type, positive_ratings)
    return bar_chart(most_common_nouns_positive, chart_config)

@sync_to_async
def asin_list_maker(user):
    analyzed_asin_list = ProcessedProductReviews.objects.filter(USER=user, reviewsanalyzedopenai__ASIN_ORIGINAL_ID__isnull=False).values('ASIN_ORIGINAL_ID').distinct()
    analyzed_asin_list = [x['ASIN_ORIGINAL_ID'] for x in analyzed_asin_list]
    return analyzed_asin_list