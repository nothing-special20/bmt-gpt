from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

import os
import re
import json
import math
import pandas as pd
from datetime import datetime

from asgiref.sync import sync_to_async

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from .functions_ra import get_reviews, get_keyword_details, process_reviews, store_processed_reviews
from .functions_other import rate_limiter, asin_list_maker, asin_list_maker_async, word_count_categories, customer_sentinment_data
from .functions_ml import most_common_words, lemmatize, sampled_phrases, create_topics, categorize_common_words
from .functions_visualizations import bar_chart
from .models import ProcessedProductReviews, Asins, ReviewsAnalyzedInternalModels, CategorizedWords, UserRequests
from .tasks import assign_topics_to_reviews

def fetch_new_asin_data(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        search_type = request.POST.get('search_type')
        search_value = request.POST.get('search_asin')
        asin_list = []
        if search_type == 'ASIN':
            asin_list = re.sub(',', ';', search_value)
            asin_list = re.sub(' ', '', asin_list)

            if ';' in asin_list:
                asin_list = asin_list.split(';')
            else:
                asin_list = [asin_list]

        if search_type == 'KEYWORD':
            keyword_details = get_keyword_details(search_value)
            keyword_details = json.loads(json.dumps(keyword_details))
            asin_list = [x['asin'] for x in keyword_details['asin_list'][0:10]]

        #Rate limit them to 20 asins per month
        if rate_limiter(user, 20):
            for asin in asin_list:
                try:
                    asin_doc = Asins(ASIN=asin)
                    asin_doc.save()
                except:
                    print(f'Error: ASIN {asin} already exists in DB')

                user_request_doc = UserRequests(
                    USER = user,
                    REQUEST_TYPE = search_type,
                    REQUEST_VALUE = search_value,
                    ASIN = Asins.objects.get(ASIN=asin),
                    REQUEST_DATE = datetime.now()
                )
                user_request_doc.save()

                for pg_num in range(1, 2):
                    raw_reviews = get_reviews(asin, pg_num)
                    proc_reviews = process_reviews(raw_reviews)
                    store_processed_reviews(proc_reviews)
                    _lemmatized_reviews = []
                    for x in proc_reviews:
                        try:
                            rev_id = ProcessedProductReviews.objects.get(ASIN_ORIGINAL_ID=x['ASIN_ORIGINAL_ID'], REVIEW_ID=x['REVIEW_ID'], reviewsanalyzedinternalmodels__LEMMATIZED_REVIEW__isnull=True)
                            _lemmatized_rev = {'REVIEW_ID': rev_id, 'LEMMA': lemmatize(x['REVIEW'])}
                            _lemmatized_reviews.append(_lemmatized_rev)
                        except:
                            print('Review already lemmatized')

                    for _rev in _lemmatized_reviews:
                        ReviewsAnalyzedInternalModels.objects.filter(PROCESSED_RECORD_ID=_rev['REVIEW_ID']).update_or_create(PROCESSED_RECORD_ID=_rev['REVIEW_ID'], LEMMATIZED_REVIEW=_rev['LEMMA'])
                        
            processed_reviews = ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID=asin).values('RECORD_ID', 'REVIEW', 'reviewsanalyzedinternalmodels__LEMMATIZED_REVIEW').distinct()
            processed_reviews = list(processed_reviews)
            lemmatized_reviews = [x['reviewsanalyzedinternalmodels__LEMMATIZED_REVIEW'] for x in processed_reviews]

            review_top_nouns_adjs_verbs = most_common_words(lemmatized_reviews, ['NOUN', 'ADJ', 'VERB'])
            Asins.objects.filter(ASIN=asin).update(MOST_COMMON_WORDS=review_top_nouns_adjs_verbs)

            sample_phrase_string = sampled_phrases(review_top_nouns_adjs_verbs, lemmatized_reviews)

            topics = create_topics(sample_phrase_string)
            topics = [x for x in topics if x != '']

            Asins.objects.filter(ASIN=asin).update(TOPICS=topics)

            assign_topics_to_reviews(processed_reviews, topics)

            categorized_words = categorize_common_words(review_top_nouns_adjs_verbs)

            for category in categorized_words:
                for word in categorized_words[category]:
                    word_doc = CategorizedWords(WORD=word, CATEGORY=category)
                    word_doc.save()

        print(f"Fetching data for {search_type}: {search_value}.")
        messages.success(request, f"Fetching data for {search_type}: {search_value}. Your report will be ready in a few minutes.")
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "showMessage": f"Fetching data for {search_type}: {search_value}."
                })
            })
    

# @login_and_team_required
async def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        
        asin_list = await asin_list_maker_async(user)

        positive_ratings = [4, 5]
        negative_ratings = [1, 2, 3]

        chart_config = {'x': 'word', 'y': 'count'}
        if request.method == 'POST' and 'retrieve-asin-data-1' in request.POST:
            asin = request.POST.get('retrieve-asin-data-1')

            if type(asin) != list:
                asin = [asin]

            word_counts = await word_count_categories(asin)
            cust_sent_data = await customer_sentinment_data(asin)
            who_counts = word_counts[word_counts['category']=='who']
            where_counts = word_counts[word_counts['category']=='where']
            when_counts = word_counts[word_counts['category']=='when']
            activity_counts = word_counts[word_counts['category']=='activities']

            who_plot = await bar_chart(who_counts, chart_config)
            where_plot = await bar_chart(where_counts, chart_config)
            when_plot = await bar_chart(when_counts, chart_config)
            activity_plot = await bar_chart(activity_counts, chart_config)

            # positive_descriptions = await review_analysis_fields(user, asin, 'DESCRIPTION', positive_ratings)
            # positive_descriptions = [x['reviewsanalyzedopenai__DESCRIPTION'] for x in positive_descriptions]
            # positive_descriptions_max_len = min(10, len(positive_descriptions))
            # positive_descriptions = positive_descriptions[:positive_descriptions_max_len]

            # negative_descriptions = await review_analysis_fields(user, asin, 'DESCRIPTION', negative_ratings)
            # negative_descriptions = [x['reviewsanalyzedopenai__DESCRIPTION'] for x in negative_descriptions]
            # negative_descriptions_max_len = min(10, len(negative_descriptions))
            # negative_descriptions = negative_descriptions[:negative_descriptions_max_len]

            context = {
                'analyzed_asin_list': asin_list,
                'selected_asin': asin,
                'who_plot': who_plot,
                'where_plot': where_plot,
                'when_plot': when_plot,
                'activity_plot': activity_plot,
                'positive_descriptions': 'positive_descriptions',
                'negative_descriptions': 'negative_descriptions',
                'cust_sent_data': cust_sent_data,
            }
        else:
            context = {
                'analyzed_asin_list': asin_list,
                'selected_asin': '',
                'who_plot': '',
                'where_plot': '',
                'when_plot': '',
                'how_often_plot': '',
                'positive_descriptions': '',
                'negative_descriptions': '',
            }
        
        return await sync_to_async(render)(request, 'web/amazon/amazon_v2.html', context)

    else:
        return render(request, 'web/landing_page.html')
    

def customer_reviews(request, team_slug):
    if request.user.is_authenticated == False:
        return render(request, 'web/landing_page.html')
    
    user = request.user.username
    asin_list = asin_list_maker(user)
    context = {'analyzed_asin_list': asin_list, 'total_pages': 0}
    results_per_page = 10
    
    if request.method == 'POST' and 'retrieve-asin-data-1' in request.POST:
        asin = request.POST.get('retrieve-asin-data-1')

        page_num = 1
        rating = [1,2,3,4,5]

        if 'page-num' in request.POST:
            page_num = int(request.POST.get('page-num'))

        if 'rating-filter' in request.POST:
            _rating = request.POST.get('rating-filter')
            if '[' in _rating:
                rating = json.loads(_rating)
            elif _rating != 'null':
                rating = [int(_rating)]

        if 'results-per-page' in request.POST:
            results_per_page = int(request.POST.get('results-per-page'))

        if type(asin) != list:
            asin = [asin]

        review_count = ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin, RATING__in=rating, REVIEW__contains='glove').count()

        rev_values = ['ASIN_ORIGINAL_ID', 'REVIEW_ID', 'RATING', 'REVIEW_DATE', 'TITLE', 'REVIEW', 'VERIFIED_PURCHASE']
        processed_reviews = list(ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin, RATING__in=rating, REVIEW__contains='glove').values(*rev_values)[((page_num-1)*results_per_page):(page_num*results_per_page)])

        context = {
            **context,
            'selected_asin': asin,
            'processed_reviews': processed_reviews,
            'review_count': review_count,
            'page_num': page_num,
            'rating': rating,
            'results_per_page': results_per_page,
        }

    return render(request, 'web/amazon/customer_reviews.html', context)