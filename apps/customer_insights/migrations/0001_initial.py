# Generated by Django 3.2.16 on 2023-06-05 13:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ASIN', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProcessedProductReviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RECORD_ID', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True, unique=True)),
                ('REVIEW_ID', models.TextField()),
                ('ASIN_VARIANT_ID', models.TextField()),
                ('REVIEWER_NAME', models.TextField()),
                ('RATING', models.IntegerField()),
                ('REVIEW_DATE', models.TextField()),
                ('REVIEW_DATE_UNIX', models.IntegerField()),
                ('TITLE', models.TextField()),
                ('REVIEW', models.TextField()),
                ('VERIFIED_PURCHASE', models.TextField()),
                ('LOAD_DATE', models.DateTimeField()),
                ('ASIN_ORIGINAL_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_insights.asins', to_field='ASIN')),
            ],
        ),
        migrations.CreateModel(
            name='UserRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('REQUEST_TYPE', models.TextField()),
                ('REQUEST_VALUE', models.TextField()),
                ('ASIN', models.TextField()),
                ('REQUEST_DATE', models.DateTimeField()),
                ('USER', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_insights.asins', to_field='ASIN')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewsAnalyzedInternalModels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TOPIC', models.TextField(blank=True, default=None, null=True)),
                ('SUB_TOPIC', models.TextField(blank=True, default=None, null=True)),
                ('QUERY_DATE', models.DateTimeField(blank=True, default=None, null=True)),
                ('PROCESSED_RECORD_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_insights.processedproductreviews', to_field='RECORD_ID')),
            ],
        ),
        migrations.CreateModel(
            name='ProductReviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('COUNTRY', models.TextField()),
                ('SORT_BY', models.TextField()),
                ('PAGE_NUM', models.IntegerField()),
                ('QUERY_DATE', models.DateTimeField()),
                ('RESPONSE', models.TextField()),
                ('ASIN', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_insights.asins', to_field='ASIN')),
            ],
        ),
    ]
