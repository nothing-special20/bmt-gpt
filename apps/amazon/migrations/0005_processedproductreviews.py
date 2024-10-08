# Generated by Django 3.2.16 on 2023-03-06 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0004_productdetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessedProductReviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('USER', models.TextField()),
                ('REVIEW_ID', models.TextField()),
                ('ASIN_ORIGINAL_ID', models.TextField()),
                ('ASIN_VARIANT_ID', models.TextField()),
                ('REVIEWER_NAME', models.TextField()),
                ('RATING', models.IntegerField()),
                ('REVIEW_DATE', models.TextField()),
                ('REVIEW_DATE_UNIX', models.IntegerField()),
                ('TITLE', models.TextField()),
                ('REVIEW', models.TextField()),
                ('VERIFIED_PURCHASE', models.TextField()),
                ('LOAD_DATE', models.DateTimeField()),
            ],
        ),
    ]
