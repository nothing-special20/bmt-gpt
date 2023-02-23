from django.db import models

class ProductReviews(models.Model):
    USER = models.TextField()
    ASIN = models.TextField()
    COUNTRY = models.TextField()
    SORT_BY = models.TextField()
    PAGE_NUM = models.IntegerField()
    QUERY_DATE = models.DateTimeField()
    RESPONSE = models.TextField()

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