# Generated by Django 2.1.15 on 2020-12-06 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_product_highestbid_userid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
