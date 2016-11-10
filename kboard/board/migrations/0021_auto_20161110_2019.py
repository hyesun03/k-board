# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-10 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0020_auto_20161110_1951'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='pages_nav_chunk_size',
            new_name='comment_pages_nav_chunk_size',
        ),
        migrations.AddField(
            model_name='board',
            name='comments_chunk_size',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='board',
            name='post_pages_nav_chunk_size',
            field=models.IntegerField(default=10),
        ),
    ]
