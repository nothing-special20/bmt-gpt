from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models.functions import Lower

import math
import re
import json
import pandas as pd
from datetime import datetime
from celery import group, chord, chain

from asgiref.sync import sync_to_async

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from .functions_ra import get_keyword_details, get_single_product_details, store_single_product_details
from .functions_other import rate_limiter, product_group_list_maker, product_group_list_maker_async, word_count_categories, customer_sentinment_data, use_product_categories, use_product_categories_async
from .functions_visualizations import bar_chart
from .models import ProcessedProductReviews, UserRequests, Asins, ProductGroups, ProcessedProductDetails
from .tasks import assign_topics_to_reviews_main, store_and_process_reviews, categorize_words, store_most_common_words, create_and_store_topics

##### JSON Responses

def fetch_new_asin_data(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        # search_type = request.POST.get('search_type')
        search_type = 'Product-Group'
        search_value = request.POST.get('search_asin')
        asin_list = []
        if search_type == 'ASIN':
            asin_list = re.sub(',', ';', search_value)
            asin_list = re.sub(' ', '', asin_list)

            if ';' in asin_list:
                asin_list = asin_list.split(';')
            else:
                asin_list = [asin_list]

        # Might reactivate this later
        # if search_type == 'KEYWORD':
        #     keyword_details = get_keyword_details(search_value)
        #     keyword_details = json.loads(json.dumps(keyword_details))
        #     asin_list = [x['asin'] for x in keyword_details['asin_list'][0:10]]

        if search_type == 'Product-Group':
            category_mappings = list(ProductGroups.objects.filter(USER=request.user.username, USER_PRODUCT_CATEGORY=search_value).distinct().values('ASIN'))
            asin_list = [x['ASIN'] for x in category_mappings]

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

                try:
                    total_reviews = ProcessedProductDetails.objects.get(ASIN_ORIGINAL_ID=Asins.objects.get(ASIN=asin)).REVIEWS['total_reviews']
                except:
                    product_details = get_single_product_details(asin)
                    store_single_product_details(product_details)
                    total_reviews = product_details['reviews']

                percent_of_reviews_with_comments = 0.15
                max_page = math.ceil(percent_of_reviews_with_comments * total_reviews / 10)

                store_and_process_reviews_jobs = [store_and_process_reviews.s(asin, pg_num) for pg_num in range(1, max_page + 1)]

                callback_chain = chain(store_most_common_words.s(), create_and_store_topics.s(), assign_topics_to_reviews_main.s())

                chord(store_and_process_reviews_jobs)(callback_chain)

                # 
            
                # need to somehow await job processing completion before continuing
                # https://ask.github.io/celery/userguide/tasksets.html#chords

                # assign_topics_to_reviews.delay(processed_reviews, topics)

                # categorize_words.delay(review_top_nouns_adjs_verbs)

            print(f"Fetching data for {search_type}: {search_value}.")
            messages.success(request, f"Fetching data for {search_type}: {search_value}. Your report will be ready in a few minutes.")

        else:
            messages.warning(request, f"Sorry - you have reached your monthly quota. Please upgrade your plan to analyze more products.")
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "showMessage": f"Fetching data for {search_type}: {search_value}."
                })
            })

def update_user_product_categories(request, team_slug):
    asin_list = request.POST.get('asins').split(';')
    asin_list = [x for x in asin_list if x != '']
    asin_list = list(set(asin_list))
    
    category = request.POST.get('category')

    ProductGroups.objects.filter(USER=request.user.username, USER_PRODUCT_CATEGORY=category).delete()

    for asin in asin_list:
        try:
            Asins(ASIN=asin).save()
        except:
            print(f'Error: ASIN {asin} already exists in DB')

        # ProductGroups.objects.filter(USER=request.user.username, USER_PRODUCT_CATEGORY=category, ASIN=Asins.objects.get(ASIN=asin)
        #     ).update_or_create(USER=request.user.username, USER_PRODUCT_CATEGORY=category, ASIN=Asins.objects.get(ASIN=asin))

        ProductGroups(USER=request.user.username, USER_PRODUCT_CATEGORY=category, ASIN=Asins.objects.get(ASIN=asin)).save()

    return JsonResponse({'status': 'success'})   

def delete_user_product_group(request, team_slug):

    category = request.POST.get('product_category')
    
    ProductGroups.objects.filter(USER_PRODUCT_CATEGORY=category, USER=request.user.username).delete()

    return JsonResponse({'status': 'Successfully deleted user product group'}) 

##### HTML Responses

# @login_and_team_required
async def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        
        # asin_list = await asin_list_maker_async(user)
        product_category_list = await product_group_list_maker_async(user)

        positive_ratings = [4, 5]
        negative_ratings = [1, 2, 3]

        chart_config = {'x': 'word', 'y': 'count'}
        if request.method == 'POST' and 'retrieve-asin-data-1' in request.POST:
            category = request.POST.get('retrieve-asin-data-1')

            asin = await use_product_categories_async(user, category)

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
                'analyzed_asin_list': product_category_list,
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
                'analyzed_asin_list': product_category_list,
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
    product_category_list = product_group_list_maker(user)

    context = {'analyzed_asin_list': product_category_list, 'total_pages': 0}
    results_per_page = 10
    
    if request.method == 'POST' and 'retrieve-asin-data-1' in request.POST:
        category = request.POST.get('retrieve-asin-data-1')
        asin = use_product_categories(user, category)

        page_num = 1
        rating = [1,2,3,4,5]
        review_search_keyword = ''

        if 'page-num' in request.POST:
            page_num = int(request.POST.get('page-num'))

        if 'rating-filter' in request.POST:
            _rating = request.POST.get('rating-filter')
            if ',' in _rating:
                rating = [1,2,3,4,5]
            elif _rating != 'null':
                rating = [int(_rating)]

        if 'results-per-page' in request.POST:
            _results_per_page = int(request.POST.get('results-per-page'))
            if _results_per_page != '':
                results_per_page = _results_per_page

        if 'review-search-keyword' in request.POST:
            review_search_keyword = request.POST.get('review-search-keyword')

        if type(asin) != list:
            asin = [asin]

        review_count = ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin, RATING__in=rating, REVIEW__contains=review_search_keyword).count()

        rev_values = ['ASIN_ORIGINAL_ID', 'REVIEW_ID', 'RATING', 'REVIEW_DATE', 'TITLE', 'REVIEW', 'VERIFIED_PURCHASE']
        processed_reviews = list(ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin, RATING__in=rating, REVIEW__contains=review_search_keyword).values(*rev_values)[((page_num-1)*results_per_page):(page_num*results_per_page)])

        context = {
            **context,
            'selected_asin': asin,
            'processed_reviews': processed_reviews,
            'review_count': review_count,
            'page_num': page_num,
            'rating': rating,
            'results_per_page': results_per_page,
            'review_search_keyword': review_search_keyword,
        }

    return render(request, 'web/amazon/customer_reviews.html', context)

def product_groups(request, team_slug):
    user = request.user.username
    product_category_list = product_group_list_maker(user)

    try:
        category_mappings = list(ProductGroups.objects.filter(USER=user).values('USER_PRODUCT_CATEGORY', 'ASIN').order_by(Lower('USER_PRODUCT_CATEGORY').desc()))

        categories = list(set([x['USER_PRODUCT_CATEGORY'] for x in category_mappings]))
        category_mappings = [{'USER_PRODUCT_CATEGORY': x, 'ASIN': [y['ASIN'] for y in category_mappings if y['USER_PRODUCT_CATEGORY'] == x]} for x in categories]
        
    except:
        category_mappings = [{'USER_PRODUCT_CATEGORY': 'Placeholder Category', 'ASIN': '123lol'}]
    
    context = { 'category_mappings': category_mappings, 'analyzed_asin_list': product_category_list,}
    return render(request, 'web/amazon/product_groups.html', context)