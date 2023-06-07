from django.conf import settings
from transformers import pipeline
import traceback

from datetime import datetime

from .models import ReviewsAnalyzedInternalModels
from .functions_ml import subtopic_labler

from celery import Celery
app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
def assign_topics_to_reviews(processed_reviews, topics):
    classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")

    for proc_review in processed_reviews:
        start_time = datetime.now()

        try:
            topic = classifier(proc_review['reviewsanalyzedinternalmodels__LEMMATIZED_REVIEW'], candidate_labels=topics)['labels'][0]
            subtopic = subtopic_labler(proc_review['REVIEW'], topic) 
            ReviewsAnalyzedInternalModels.objects.filter(PROCESSED_RECORD_ID=proc_review['RECORD_ID']).update(TOPIC=topic, SUB_TOPIC=subtopic)
        except:
            print(traceback.format_exc())
            
        print('Total time taken: ', datetime.now() - start_time)