# Generated by Django 3.2.16 on 2023-03-06 23:31

from django.db import migrations, models
import django.db.models.deletion
import uuid

def create_uuid(apps, schema_editor):
    processed_product_reviews = apps.get_model('amazon', 'processedproductreviews')
    for review in processed_product_reviews.objects.all():
        review.RECORD_ID = uuid.uuid4()
        review.save()

class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0007_auto_20230306_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='processedproductreviews',
            name='RECORD_ID',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(create_uuid),
        migrations.AlterField(
            model_name='processedproductreviews',
            name='RECORD_ID',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
        ),
        migrations.AddField(
            model_name='reviewsanalyzedinternalmodels',
            name='PROCESSED_RECORD_ID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='amazon.processedproductreviews', to_field='RECORD_ID'),
        ),
    ]
