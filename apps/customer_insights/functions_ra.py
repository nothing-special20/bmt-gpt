import json
import os
import environ
import requests
import time
import traceback

from pathlib import Path

from datetime import datetime

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from .models import Asins, ProcessedProductReviews

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR,  ".env"))

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

#####RA Response ETL
def process_reviews(raw_reviews):
    _reviews = json.loads(raw_reviews)
    processed_review_list = []
    try:
        reviews = _reviews['result']
        for rev in reviews:
            processed_review = {
                'REVIEW_ID': rev['id'],
                'ASIN_ORIGINAL_ID': rev['asin']['original'],
                'ASIN_VARIANT_ID': rev['asin']['variant'],
                'REVIEWER_NAME': rev['name'],
                'RATING': rev['rating'],
                'REVIEW_DATE': rev['date']['date'],
                'REVIEW_DATE_UNIX': rev['date']['unix'],
                'TITLE': rev['title'],
                'REVIEW': rev['review'],
                'VERIFIED_PURCHASE': rev['verified_purchase']
            }
            processed_review_list.append(processed_review)

    except:
        print(traceback.format_exc())

    return processed_review_list


def store_processed_reviews(reviews):
    for rev in reviews:
        doc = ProcessedProductReviews(
            REVIEW_ID = rev['REVIEW_ID'],
            ASIN_REVIEW_CONCAT_ID = rev['ASIN_ORIGINAL_ID'] + '~' + rev['REVIEW_ID'],
            ASIN_ORIGINAL_ID = Asins.objects.get(ASIN=rev['ASIN_ORIGINAL_ID']),
            ASIN_VARIANT_ID = rev['ASIN_VARIANT_ID'],
            REVIEWER_NAME = rev['REVIEWER_NAME'],
            RATING = rev['RATING'],
            REVIEW_DATE = rev['REVIEW_DATE'],
            REVIEW_DATE_UNIX = rev['REVIEW_DATE_UNIX'],
            TITLE = rev['TITLE'],
            REVIEW = rev['REVIEW'],
            VERIFIED_PURCHASE = rev['VERIFIED_PURCHASE'],
            LOAD_DATE = datetime.now(),
        )
        try:
            doc.save()
        except:
            print(traceback.format_exc())