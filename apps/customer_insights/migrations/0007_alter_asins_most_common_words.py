# Generated by Django 3.2.16 on 2023-06-06 15:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_insights', '0006_auto_20230606_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asins',
            name='MOST_COMMON_WORDS',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None),
        ),
    ]
