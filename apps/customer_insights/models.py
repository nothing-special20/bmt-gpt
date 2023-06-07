from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField

class Asins(models.Model):
    ASIN = models.TextField(unique=True)
    MOST_COMMON_WORDS = ArrayField(models.TextField(), null=True)
    TOPICS = ArrayField(models.TextField(), null=True)

class UserRequests(models.Model):
    USER = models.TextField()
    REQUEST_TYPE = models.TextField()
    REQUEST_VALUE = models.TextField()
    ASIN = models.ForeignKey(Asins, to_field='ASIN', on_delete=models.CASCADE, db_column='ASIN')
    REQUEST_DATE = models.DateTimeField()

class ProductReviews(models.Model):
    ASIN = models.ForeignKey(Asins, to_field='ASIN', on_delete=models.CASCADE)
    COUNTRY = models.TextField()
    SORT_BY = models.TextField()
    PAGE_NUM = models.IntegerField()
    QUERY_DATE = models.DateTimeField()
    RESPONSE = models.TextField()

# ASIN + Review ID pairs should be unique
class ProcessedProductReviews(models.Model):
    RECORD_ID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    ASIN_REVIEW_CONCAT_ID = models.TextField(unique=True, null=True)
    REVIEW_ID = models.TextField()
    ASIN_ORIGINAL_ID = models.ForeignKey(Asins, to_field='ASIN', on_delete=models.CASCADE)
    ASIN_VARIANT_ID = models.TextField()
    REVIEWER_NAME = models.TextField()
    RATING = models.IntegerField()
    REVIEW_DATE = models.TextField()
    REVIEW_DATE_UNIX = models.IntegerField()
    TITLE = models.TextField()
    REVIEW = models.TextField()
    VERIFIED_PURCHASE = models.TextField()
    LOAD_DATE = models.DateTimeField()

class ReviewsAnalyzedInternalModels(models.Model):
    PROCESSED_RECORD_ID = models.OneToOneField(ProcessedProductReviews, to_field='RECORD_ID', on_delete=models.CASCADE)
    LEMMATIZED_REVIEW = models.TextField(null=True)
    TOPIC = models.TextField(default=None, blank=True, null=True)
    SUB_TOPIC = models.TextField(default=None, blank=True, null=True)
    QUERY_DATE = models.DateTimeField(default=None, blank=True, null=True)

class CategorizedWords(models.Model):
    WORD = models.TextField()
    CATEGORY = models.TextField()