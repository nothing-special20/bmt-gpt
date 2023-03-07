from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# from .functions import interpret_text, read_word_doc
# from .models import DocQueries, IndexQueries
# from django.templatetags.static import static
import re
import json
import pandas as pd

from asgiref.sync import sync_to_async

from django.conf import settings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from django.contrib.staticfiles.storage import staticfiles_storage

from .functions import asin_gpt_data, prompts, rate_limiter, get_keyword_details, review_analysis_most_common_words, create_word_bar_chart
from .models import ReviewsAnalyzed

from .tasks import prep_all_gpt_data

def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        analyzed_asin_list = ReviewsAnalyzed.objects.filter(USER=user).values('ASIN').distinct()
        analyzed_asin_list = [x['ASIN'] for x in analyzed_asin_list]

        if request.method == 'POST' and 'search-asin' in request.POST and 'search-type' in request.POST:
            search_type = request.POST.get('search-type')
            search_value = request.POST.get('search-asin')
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
                # prep_all_gpt_data.delay(user, asin_list)
                prep_all_gpt_data(user, asin_list)

        if request.method == 'POST' and 'retrieve-asin-data-1' in request.POST:
            asin = request.POST.get('retrieve-asin-data-1')
            asin_compare = request.POST.get('retrieve-asin-data-2')
            
            asin_one_data = asin_gpt_data(user, asin, prompts)

            try:
                asin_two_data = asin_gpt_data(user, asin_compare, prompts)
            except:
                asin_two_data = {}

            return render(request, 'web/amazon/amazon_demo.html', {
                'analyzed_asin_list': analyzed_asin_list,
                'asin_one_data': asin_one_data,
                'asin_two_data': asin_two_data,
            })

        return render(request, 'web/amazon/amazon_demo.html', {
            'analyzed_asin_list': analyzed_asin_list,
        })
    else:
        return render(request, 'web/landing_page.html')

# @login_and_team_required
async def main_v2(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        # analyzed_asin_list = ReviewsAnalyzedInternalModels.objects.filter(USER=user).values('ASIN_ORIGINAL_ID').distinct()
        # analyzed_asin_list = [x['ASIN_ORIGINAL_ID'] for x in analyzed_asin_list]
        # asin = analyzed_asin_list[0]
        asin = 'B01N1VV36N'

        positive_ratings = [4, 5]
        negative_ratings = [1, 2, 3]

        chart_config = {'x': 'word', 'y': 'count'}

        

        positive_noun_plot = await create_word_bar_chart(user, asin, 'NOUNS', positive_ratings, chart_config)
        # positive_adjectives_plot = await create_word_bar_chart(user, asin, 'ADJECTIVES', positive_ratings, chart_config)
        # negative_noun_plot = create_word_bar_chart(user, asin, 'NOUNS', negative_ratings, chart_config)
        # positive_adjectives_plot = await create_word_bar_chart(user, asin, 'ADJECTIVES', negative_ratings, chart_config)

        # context['positive_noun_plot'] = positive_noun_plot
        context = {
            'analyzed_asin_list': [],
            # 'positive_noun_plot': 'Loading Chart...',
            'positive_noun_plot': positive_noun_plot,
        }
        
        return await sync_to_async(render)(request, 'web/amazon/amazon_v2.html', context)

    else:
        return render(request, 'web/landing_page.html')