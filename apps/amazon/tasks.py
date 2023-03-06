from django.conf import settings
from celery import Celery
from celery import group
# from django.core.management import call_command
from datetime import datetime
import math
import json

from .functions import get_single_product_detail, save_product_detail, store_gpt_results, prompts, get_reviews, save_reviews, process_reviews
from .functions_analysis import find_types_of_words
from .models import ProcessedProductReviews, ReviewsAnalyzedInternalModels

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
def store_reviews(user, asin, pg_num):
    reviews = get_reviews(asin, pg_num)
    save_reviews(user, asin, pg_num, reviews)
    process_reviews(user, reviews)

@app.task
def extract_nouns_adjectives_from_reviews(user, asin):
    reviews = list(ProcessedProductReviews.objects.filter(USER=user, ASIN_ORIGINAL_ID=asin).all().distinct().values())
    reviews = [review for review in reviews if review['VERIFIED_PURCHASE'] == 'True']

    for review in reviews:
        review_text = review['REVIEW']
        nouns = find_types_of_words(review_text, 'NOUN')
        adjectives = find_types_of_words(review_text, 'ADJ')
        
        doc = ReviewsAnalyzedInternalModels(
            USER = user,
            REVIEW_ID = review['REVIEW_ID'],
            ASIN_ORIGINAL_ID = review['ASIN_ORIGINAL_ID'],
            ASIN_VARIANT_ID = review['ASIN_VARIANT_ID'],
            NOUNS = nouns,
            ADJECTIVES = adjectives,
            QUERY_DATE = datetime.now()
        )

        doc.save()

@app.task
def prep_all_gpt_data(user, asin_list):
    for asin in asin_list:
        print(asin)
        product_detail = get_single_product_detail(asin)
        save_product_detail(user, asin, product_detail)

        total_reviews = json.loads(product_detail)['result'][0]['reviews']['total_reviews']

        max_page = min(math.ceil(total_reviews / 10), 50)
        
        job_list = group([store_reviews.subtask((user, asin, pg_num)) for pg_num in range(1, max_page + 1)])
        
        job_list.apply()

    job_list_extract_nouns_adjectives_from_reviews = group([extract_nouns_adjectives_from_reviews.subtask((user, asin)) for asin in asin_list])
    job_list_extract_nouns_adjectives_from_reviews.apply()

    # for asin in asin_list:
    #     extract_nouns_adjectives_from_reviews(user, asin) 

    store_gpt_results(user, asin_list, prompts)