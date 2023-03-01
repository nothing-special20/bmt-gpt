from django.conf import settings
from celery import Celery
from celery import group
# from django.core.management import call_command
import multiprocessing
from itertools import repeat
import math
import json

from .functions import get_single_product_detail, save_product_detail, store_gpt_results, split_list_into_sublists, prompts, get_reviews, save_reviews

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
def store_reviews(user, asin, pg_num):
    reviews = get_reviews(asin, pg_num)
    save_reviews(user, asin, pg_num, reviews)

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

    store_gpt_results(user, asin_list, prompts)