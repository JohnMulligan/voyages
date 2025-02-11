# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contribute', '0013_auto_20161009_0504'),
    ]

    operations = [
        migrations.AddField(
            model_name='interimvoyage',
            name='persisted_form_data',
            field=models.TextField(
                help_text='Auxiliary form data that is persisted in JSON '
                'format',
                max_length=10000,
                null=True,
                blank=True),
        ),
    ]
