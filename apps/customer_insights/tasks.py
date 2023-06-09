from django.conf import settings
from transformers import pipeline
import traceback
from celery import group

from datetime import datetime

from .models import ReviewsAnalyzedInternalModels, ProcessedProductReviews, CategorizedWords
from .functions_ml import subtopic_labler, lemmatize, categorize_common_words
from .functions_ra import get_reviews, process_reviews, store_processed_reviews

from celery import Celery
app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
def assign_topics_to_reviews(processed_reviews, topics):
    classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")

    for proc_review in processed_reviews:
        _assign_topic_to_review(classifier, proc_review, topics)
        
@app.task
def _assign_topic_to_review(classifier, proc_review, topics):
    start_time = datetime.now()
    try:
        topic = classifier(proc_review['reviewsanalyzedinternalmodels__LEMMATIZED_REVIEW'], candidate_labels=topics)['labels'][0]
        subtopic = subtopic_labler(proc_review['REVIEW'], topic) 
        ReviewsAnalyzedInternalModels.objects.filter(PROCESSED_RECORD_ID=proc_review['RECORD_ID']).update(TOPIC=topic, SUB_TOPIC=subtopic)
    except:
        print(traceback.format_exc())
    
    time_taken = str(datetime.now() - start_time)
    lemma_length = len(proc_review['reviewsanalyzedinternalmodels__LEMMATIZED_REVIEW'])
    label_length = len(topics)

    print(f'Topic classification for lemma with {lemma_length} characters and {label_length} topics took: {time_taken}')

@app.task
def store_and_process_reviews(asin, pg_num):
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


@app.task
def categorize_words(review_top_nouns_adjs_verbs):
    categorized_words = categorize_common_words(review_top_nouns_adjs_verbs)
    for category in categorized_words:
        for word in categorized_words[category]:
            word_doc = CategorizedWords(WORD=word, CATEGORY=category)
            word_doc.save()