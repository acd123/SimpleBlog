# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20160524_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='status',
            field=models.BooleanField(default=False, verbose_name=b'\xe7\x8a\xb6\xe6\x80\x81'),
        ),
    ]
