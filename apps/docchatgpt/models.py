from django.db import models

class DocQueries(models.Model):
    USER = models.TextField()
    DOC_NAME = models.TextField(null=True)
    DOC_TEXT = models.TextField()
    QUERY = models.TextField()
    GPT_RESPONSE = models.TextField()
    COMPLETION_TOKENS = models.IntegerField()
    PROMPT_TOKENS = models.IntegerField()
    QUERY_DATE = models.DateTimeField()

class IndexQueries(models.Model):
    USER = models.TextField()
    INDEX_NAME = models.TextField()
    QUERY = models.TextField()
    GPT_RESPONSE = models.TextField()
    TOTAL_LLM_TOKEN_USAGE = models.IntegerField()
    TOTAL_EMBEDDING_TOKEN_USAGE = models.IntegerField()
    QUERY_DATE = models.DateTimeField()