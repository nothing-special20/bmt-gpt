from django.conf import settings
from celery import Celery
from celery import group
# from django.core.management import call_command
from datetime import datetime
import math
import json
import re

from .functions import get_single_product_detail, save_product_detail, store_gpt_results, prompts, get_reviews, save_reviews, process_reviews, gpt_analyze_reviews
from .functions_analysis import find_types_of_words
from .models import ProcessedProductReviews, ReviewsAnalyzedInternalModels, ReviewsAnalyzedOpenAI

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

single_review_partial_prompt = "Read the following review and return the following in a JSON object, with keys noted in single quotes (note, if the question cannot be answered, answer 'NA'): 1) 'who': the people mentioned in the review, separated by a comma. 2) 'when': Any dates mentioned 3) 'where': Where they use it 4) 'description': A brief description of how they feel about the product. 5) 'how_often' How often the use it. 6) 'motivation': why they bought it. 7) 'expectations': what the reviewer expects from the product. The review: "

@app.task
def store_reviews(user, asin, pg_num):
    reviews = get_reviews(asin, pg_num)
    results = json.loads(reviews)['result']
    if len(results) > 0:
        save_reviews(user, asin, pg_num, reviews)
        process_reviews(user, reviews)

@app.task
def store_and_analyze_reviews(user, asin, pg_num):
    reviews = get_reviews(asin, pg_num)
    try:
        result = json.loads(reviews)['result']
        if len(result) > 0:
            save_reviews(user, asin, pg_num, reviews)
            processed_reviews = process_reviews(user, reviews)

            job_list_extract_nouns_adjectives_from_reviews = group([extract_nouns_adjectives_from_reviews.subtask((review, user)) for review in processed_reviews])
            job_list_extract_nouns_adjectives_from_reviews.apply_async()

            job_list_store_gpt_single_review_analysis = group([store_gpt_single_review_analysis.subtask((user, single_review_partial_prompt, review)) for review in reviews])
            job_list_store_gpt_single_review_analysis.appl_async()

    except:
        print('No reviews found')
        print(reviews)

@app.task
def extract_nouns_adjectives_from_reviews(review, user):
     if review['VERIFIED_PURCHASE'] in ['True', True]:
        review_text = review['REVIEW']
        nouns = find_types_of_words(review_text, 'NOUN')
        adjectives = find_types_of_words(review_text, 'ADJ')
        
        doc = ReviewsAnalyzedInternalModels(
            PROCESSED_RECORD_ID=ProcessedProductReviews.objects.get(RECORD_ID=review['RECORD_ID']),
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
def store_gpt_single_review_analysis(user, partial_prompt, review):
    gpt_result = gpt_analyze_reviews(review['REVIEW'], '', partial_prompt)
    gpt_query_result = json.loads(re.sub("'", '"', gpt_result['gpt_evaluation']))

    doc = ReviewsAnalyzedOpenAI(
        PROCESSED_RECORD_ID = ProcessedProductReviews.objects.get(RECORD_ID=review['RECORD_ID']),
        USER = user,
        REVIEW_ID = review['REVIEW_ID'],
        ASIN_ORIGINAL_ID = review['ASIN_ORIGINAL_ID'],
        ASIN_VARIANT_ID = review['ASIN_VARIANT_ID'],
        PROMPT = partial_prompt,
        GPT_RESPONSE = gpt_result['gpt_evaluation'],
        WHO = gpt_query_result['who'],
        WHERE = gpt_query_result['where'],
        WHEN = gpt_query_result['when'],
        DESCRIPTION = gpt_query_result['description'],
        HOW_OFTEN = gpt_query_result['how_often'],
        MOTIVATION = gpt_query_result['motivation'],
        EXPECTATIONS = gpt_query_result['expectations'],
        COMPLETION_TOKENS = gpt_result['completion_tokens'],
        PROMPT_TOKENS = gpt_result['prompt_tokens'],
        QUERY_DATE = datetime.now()
    )

    doc.save()

@app.task
def prep_all_gpt_data(user, asin_list):
    for asin in asin_list:
        print(asin)
        product_detail = get_single_product_detail(asin)
        save_product_detail(user, asin, product_detail)

        total_reviews = product_detail['reviews']['total_reviews']

        #not all reviews have comments, so we need to limit the number of pages we scrape
        #need a better estimate later - this will do
        percent_of_reviews_with_comments = 0.15
        max_page = min(math.ceil(percent_of_reviews_with_comments * total_reviews / 10), 200)
        
        job_list = group([store_and_analyze_reviews.subtask((user, asin, pg_num)) for pg_num in range(1, max_page + 1)])
        job_list.apply_async()

    store_gpt_results(user, asin_list, prompts)