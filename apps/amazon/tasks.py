from django.conf import settings
from celery import Celery
# from django.core.management import call_command
import multiprocessing
from itertools import repeat
import math
import json

from .functions import get_single_product_detail, save_product_detail, store_gpt_results, split_list_into_sublists, store_reviews, prompts

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
def prep_all_gpt_data(user, asin_list):
    for asin in asin_list:
        print(asin)
        product_detail = get_single_product_detail(asin)
        save_product_detail(user, asin, product_detail)

        total_reviews = json.loads(product_detail)['result'][0]['reviews']['total_reviews']

        max_page = min(math.ceil(total_reviews / 10), 50)
        
        num_processes = settings.NUM_PARALLEL_PROCESSORS
        sublists = split_list_into_sublists(range(1, max_page + 1), num_processes)
        pool = multiprocessing.Pool(processes=num_processes)
        pool.starmap(store_reviews, zip(repeat(user), repeat(asin), sublists))

    store_gpt_results(user, asin_list, prompts)