# Generated by Django 4.2.3 on 2023-08-11 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement_feed', '0002_rename_advertisements_advertisement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='deleted_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
