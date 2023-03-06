from django.db import models
from django.contrib.postgres.fields import ArrayField

import uuid

class ProductReviews(models.Model):
    USER = models.TextField()
    ASIN = models.TextField()
    COUNTRY = models.TextField()
    SORT_BY = models.TextField()
    PAGE_NUM = models.IntegerField()
    QUERY_DATE = models.DateTimeField()
    RESPONSE = models.TextField()

class ProcessedProductReviews(models.Model):
    RECORD_ID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    USER = models.TextField()
    REVIEW_ID = models.TextField()
    ASIN_ORIGINAL_ID = models.TextField()
    ASIN_VARIANT_ID = models.TextField()
    REVIEWER_NAME = models.TextField()
    RATING = models.IntegerField()
    REVIEW_DATE = models.TextField()
    REVIEW_DATE_UNIX = models.IntegerField()
    TITLE = models.TextField()
    REVIEW = models.TextField()
    VERIFIED_PURCHASE = models.TextField()
    LOAD_DATE = models.DateTimeField()

class ProductDetails(models.Model):
    USER = models.TextField()
    ASIN = models.TextField()
    COUNTRY = models.TextField()
    RESPONSE = models.TextField()
    QUERY_DATE = models.DateTimeField()

class ReviewsAnalyzed(models.Model):
    USER = models.TextField()
    ASIN = models.TextField(default=None, blank=True, null=True)
    PROMPT = models.TextField()
    QUERY = models.TextField()
    GPT_RESPONSE = models.JSONField()
    COMPLETION_TOKENS = models.IntegerField()
    PROMPT_TOKENS = models.IntegerField()
    QUERY_DATE = models.DateTimeField()

class ReviewsAnalyzedInternalModels(models.Model):
    PROCESSED_RECORD_ID = models.ForeignKey(ProcessedProductReviews, to_field='RECORD_ID', on_delete=models.CASCADE, null=True)
    USER = models.TextField()
    REVIEW_ID = models.TextField()
    ASIN_ORIGINAL_ID = models.TextField(default=None, blank=True, null=True)
    ASIN_VARIANT_ID = models.TextField(default=None, blank=True, null=True)
    NOUNS = ArrayField(models.TextField())
    ADJECTIVES = ArrayField(models.TextField())
    QUERY_DATE = models.DateTimeField(default=None, blank=True, null=True)