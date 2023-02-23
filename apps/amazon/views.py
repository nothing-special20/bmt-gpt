from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
import re
import json

# from .functions import interpret_text, read_word_doc
# from .models import DocQueries, IndexQueries
# from django.templatetags.static import static

from django.conf import settings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from django.contrib.staticfiles.storage import staticfiles_storage

from .functions import get_reviews, save_reviews, agg_reviews_for_gpt, gpt_analyze_reviews, save_gpt_results, get_single_product_detail, save_product_detail, asin_gpt_data
from .models import ProductReviews, ReviewsAnalyzed, ProductDetails


like_partial_prompt = "From the following reviews, Write the Top 5 things people like about the product, each review is separated by a semicolon: "
dislike_partial_prompt = "From the following reviews, Write the Top 5 things people dislike about the product, each review is separated by a semicolon: "
description_partial_prompt = "From the following reviews, Write the Top 5 phrases people used to describe the product, each review is separated by a semicolon: "

prompts = {
    'dislike_partial_prompt': dislike_partial_prompt,
    'like_partial_prompt': like_partial_prompt,
    'description_partial_prompt': description_partial_prompt,
}

def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        asin_list = ReviewsAnalyzed.objects.filter(USER=user).values('ASIN').distinct()
        asin_list = [x['ASIN'] for x in asin_list]

        if request.method == 'POST' and 'search-asin' in request.POST:
            print('search-asin')
            asin = request.POST.get('search-asin')
            print(asin)

            product_detail = get_single_product_detail(asin)
            save_product_detail(user, asin, product_detail)

            for pg_num in range(1, 15):
                reviews = get_reviews(asin, pg_num)
                save_reviews(user, asin, pg_num, reviews)
        
            agg_reviews = agg_reviews_for_gpt(user, asin)
            
            dislikes = gpt_analyze_reviews(agg_reviews, asin, dislike_partial_prompt)
            save_gpt_results(user, asin, dislike_partial_prompt, dislikes)

            likes = gpt_analyze_reviews(agg_reviews, asin, like_partial_prompt)
            save_gpt_results(user, asin, like_partial_prompt, likes)

            descriptions = gpt_analyze_reviews(agg_reviews, asin, description_partial_prompt)
            save_gpt_results(user, asin, description_partial_prompt, descriptions)

        if request.method == 'POST' and 'retrieve-asin-data' in request.POST:
            asin = request.POST.get('retrieve-asin-data')
            asin_compare = request.POST.get('retrieve-asin-data-2')
            
            asin_one_data = asin_gpt_data(user, asin, prompts)

            try:
                asin_two_data = asin_gpt_data(user, asin_compare, prompts)
            except:
                asin_two_data = {}

            return render(request, 'web/amazon/amazon_demo.html', {
                'asin_list': asin_list,
                'asin_one_data': asin_one_data,
                'asin_two_data': asin_two_data,
            })

        return render(request, 'web/amazon/amazon_demo.html', {
            'asin_list': asin_list,
        })
    else:
        return render(request, 'web/landing_page.html')
