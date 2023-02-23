from django.conf import settings
from celery import Celery
# from django.core.management import call_command
import multiprocessing
from itertools import repeat

from .functions import get_single_product_detail, save_product_detail, store_gpt_results, split_list_into_sublists, store_reviews, prompts

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
def prep_all_gpt_data(user, asin):
    product_detail = get_single_product_detail(asin)
    save_product_detail(user, asin, product_detail)

    sublists = split_list_into_sublists(range(1, 16), 6)

    pool = multiprocessing.Pool(processes=6)
    pool.starmap(store_reviews, zip(repeat(user), repeat(asin), sublists))

    store_gpt_results(user, asin, prompts)