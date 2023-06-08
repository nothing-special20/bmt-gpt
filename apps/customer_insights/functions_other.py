from asgiref.sync import sync_to_async
from datetime import datetime
import re
from django.db.models import Count

import pandas as pd

from .models import Asins, ProcessedProductReviews, CategorizedWords, ReviewsAnalyzedInternalModels
from .functions_ml import most_common_words, lemmatize

def rate_limiter(user, asin_limit):
    # now = datetime.now()
    # current_month = now.month
    # current_year = now.year

    # all_user_asins = UserRequests.objects.filter(USER=user, REQUEST_DATE__year=current_year, REQUEST_DATE__month=current_month).values('ASIN').distinct()
    # all_user_asins = [x['ASIN'] for x in list(all_user_asins)]

    # return len(all_user_asins) < asin_limit
    return True

def asin_list_maker(user):
    analyzed_asin_list = Asins.objects.filter(userrequests__USER=user).values('ASIN').distinct()
    analyzed_asin_list = list(analyzed_asin_list)
    analyzed_asin_list = [x['ASIN'] for x in analyzed_asin_list]
    return analyzed_asin_list

@sync_to_async
def asin_list_maker_async(user):
    return asin_list_maker(user)

@sync_to_async
def word_count_categories(asin):
    rev_id = ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin)
    reviews = ReviewsAnalyzedInternalModels.objects.filter(PROCESSED_RECORD_ID__in=rev_id).values('LEMMATIZED_REVIEW')
    reviews = list(reviews)

    lemmatized_reviews = [re.sub(r'[^\w\s]', '', str(x['LEMMATIZED_REVIEW'])) for x in reviews]
    lemmatized_reviews = [lemmatize(x) for x in lemmatized_reviews]

    review_top_nouns_adjs_verbs = most_common_words(lemmatized_reviews, ['NOUN', 'ADJ', 'VERB'])
    review_top_nouns_adjs_verbs = pd.DataFrame(review_top_nouns_adjs_verbs, columns=['word', 'count'])
    review_top_nouns_adjs_verbs['word'] = [str(x) for x in review_top_nouns_adjs_verbs['word']]

    word_categories = CategorizedWords.objects.values('WORD', 'CATEGORY').distinct()
    word_categories = list(word_categories)
    word_categories = pd.DataFrame(word_categories)
    word_categories.columns = ['word', 'category']
    word_categories['word'] = [str(x) for x in word_categories['word']]

    final = pd.merge(review_top_nouns_adjs_verbs, word_categories, on='word', how='left')
    final = final[[len(x) > 1 for x in final['word']]]
    
    return final

@sync_to_async
def customer_sentinment_data(asin):
    topic_counts = ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin).values('reviewsanalyzedinternalmodels__TOPIC').annotate(count=Count('RECORD_ID'))
    topic_counts = list(topic_counts)
    topic_counts = sorted(topic_counts, key=lambda x: x['count'], reverse=True)
    topic_counts = pd.DataFrame(topic_counts)

    sample_sub_topics = ProcessedProductReviews.objects.filter(ASIN_ORIGINAL_ID__in=asin).values('reviewsanalyzedinternalmodels__TOPIC', 'reviewsanalyzedinternalmodels__SUB_TOPIC').distinct()
    sample_sub_topics = list(sample_sub_topics)
    sample_sub_topics = pd.DataFrame(sample_sub_topics)
    sample_sub_topics = sample_sub_topics.groupby('reviewsanalyzedinternalmodels__TOPIC').head(3)#['reviewsanalyzedinternalmodels__SUB_TOPIC'].apply(lambda x: ', '.join(x)).reset_index()
    sample_sub_topics = sample_sub_topics.groupby('reviewsanalyzedinternalmodels__TOPIC')['reviewsanalyzedinternalmodels__SUB_TOPIC'].apply(', '.join).reset_index()
    #concatenate the subtopics for each topic
    # test = sample_sub_topics.to_dict('records')

    final = pd.merge(topic_counts, sample_sub_topics, on='reviewsanalyzedinternalmodels__TOPIC', how='left')

    final.rename(columns={'reviewsanalyzedinternalmodels__TOPIC': 'topic', 'reviewsanalyzedinternalmodels__SUB_TOPIC': 'sub_topic'}, inplace=True)

    final = final.to_dict('records')

    return final
