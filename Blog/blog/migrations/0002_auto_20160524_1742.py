# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='desc',
            field=models.CharField(max_length=200, verbose_name=b'\xe6\x96\x87\xe7\xab\xa0\xe6\x8f\x8f\xe8\xbf\xb0'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=100, verbose_name=b'\xe6\x96\x87\xe7\xab\xa0\xe6\xa0\x87\xe9\xa2\x98'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default=b'static/img/default.png', upload_to=b'avatar/%Y/%m', max_length=200, blank=True, null=True, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\xa4\xb4\xe5\x83\x8f'),
        ),
    ]
