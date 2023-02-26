from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# from .functions import interpret_text, read_word_doc
# from .models import DocQueries, IndexQueries
# from django.templatetags.static import static

from django.conf import settings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from django.contrib.staticfiles.storage import staticfiles_storage

from .functions import asin_gpt_data, prompts, rate_limiter
from .models import ReviewsAnalyzed

from .tasks import prep_all_gpt_data

def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        analyzed_asin_list = ReviewsAnalyzed.objects.filter(USER=user).values('ASIN').distinct()
        analyzed_asin_list = [x['ASIN'] for x in analyzed_asin_list]

        if request.method == 'POST' and 'search-asin' in request.POST:
            print('search-asin')
            asin_list = request.POST.get('search-asin')
            if ';' in asin_list:
                asin_list = asin_list.split(';')
            else:
                asin_list = [asin_list]

            #Rate limit them to 100 asins per month
            if rate_limiter(user, 100):
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
