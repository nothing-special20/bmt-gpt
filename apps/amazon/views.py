from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

# from .functions import interpret_text, read_word_doc
# from .models import DocQueries, IndexQueries
# from django.templatetags.static import static
import re
import json

from asgiref.sync import sync_to_async

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from .functions import asin_gpt_data, prompts, rate_limiter, get_keyword_details, create_word_bar_chart, review_analysis_fields, asin_list_maker
from .models import ReviewsAnalyzed

from .tasks import prep_all_gpt_data

def fetch_new_asin_data(request, team_slug):
    print('lol it worked')
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
            prep_all_gpt_data.delay(user, asin_list)

        print(f"Fetching data for {search_type}: {search_value}.")
        messages.success(request, f"Fetching data for {search_type}: {search_value}. Your report will be ready in a few minutes.")
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "showMessage": f"Fetching data for {search_type}: {search_value}."
                })
            })

def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        analyzed_asin_list = ReviewsAnalyzed.objects.filter(USER=user).values('ASIN').distinct()
        analyzed_asin_list = [x['ASIN'] for x in analyzed_asin_list]

        if request.method == 'POST' and 'search-asin' in request.POST and 'search-type' in request.POST:
            fetch_new_asin_data(request, team_slug)

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
        
        asin_list = await asin_list_maker(user)

        positive_ratings = [4, 5]
        negative_ratings = [1, 2, 3]

        chart_config = {'x': 'word', 'y': 'count'}
        if request.method == 'POST' and 'retrieve-asin-data-1' in request.POST:
            asin = request.POST.get('retrieve-asin-data-1')

            who_plot = await create_word_bar_chart(user, asin, 'WHO', positive_ratings, chart_config)
            where_plot = await create_word_bar_chart(user, asin, 'WHERE', positive_ratings, chart_config)
            when_plot = await create_word_bar_chart(user, asin, 'WHEN', negative_ratings, chart_config)
            how_often_plot = await create_word_bar_chart(user, asin, 'HOW_OFTEN', negative_ratings, chart_config)

            positive_descriptions = await review_analysis_fields(user, asin, 'DESCRIPTION', positive_ratings)
            positive_descriptions = [x['reviewsanalyzedopenai__DESCRIPTION'] for x in positive_descriptions]
            positive_descriptions_max_len = min(10, len(positive_descriptions))
            positive_descriptions = positive_descriptions[:positive_descriptions_max_len]

            negative_descriptions = await review_analysis_fields(user, asin, 'DESCRIPTION', negative_ratings)
            negative_descriptions = [x['reviewsanalyzedopenai__DESCRIPTION'] for x in negative_descriptions]
            negative_descriptions_max_len = min(10, len(negative_descriptions))
            negative_descriptions = negative_descriptions[:negative_descriptions_max_len]

            context = {
                'analyzed_asin_list': asin_list,
                'selected_asin': asin,
                'who_plot': who_plot,
                'where_plot': where_plot,
                'when_plot': when_plot,
                'how_often_plot': how_often_plot,
                'positive_descriptions': positive_descriptions,
                'negative_descriptions': negative_descriptions,
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