from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# from .functions import interpret_text, read_word_doc
# from .models import DocQueries, IndexQueries
# from django.templatetags.static import static

from django.conf import settings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from django.contrib.staticfiles.storage import staticfiles_storage

from .functions import get_reviews, save_reviews, asin_gpt_data, prompts
from .models import ReviewsAnalyzed

from .tasks import prep_all_gpt_data


def main(request, team_slug):
    if request.user.is_authenticated:
        user = request.user.username
        asin_list = ReviewsAnalyzed.objects.filter(USER=user).values('ASIN').distinct()
        asin_list = [x['ASIN'] for x in asin_list]

        if request.method == 'POST' and 'search-asin' in request.POST:
            print('search-asin')
            asin = request.POST.get('search-asin')
            print(asin)

            prep_all_gpt_data(user, asin)

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
