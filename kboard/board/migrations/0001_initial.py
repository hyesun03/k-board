# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-15 14:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(default='', max_length=100, unique=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('posts_chunk_size', models.IntegerField(default=10)),
                ('post_pages_nav_chunk_size', models.IntegerField(default=10)),
                ('comments_chunk_size', models.IntegerField(default=5)),
                ('comment_pages_nav_chunk_size', models.IntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('content', models.TextField(default='')),
                ('is_deleted', models.BooleanField(default=False)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Account')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EditedPostHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(default='', max_length=100)),
                ('content', models.TextField(default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField(default='')),
                ('is_deleted', models.BooleanField(default=False)),
                ('page_view_count', models.IntegerField(default=0)),
                ('like_count', models.IntegerField(default=0)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Account')),
                ('board', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='board.Board')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='editedposthistory',
            name='post',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='board.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='board.Post'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='editedPostHistory',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='board.EditedPostHistory'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='board.Post'),
        ),
    ]
