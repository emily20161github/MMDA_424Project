from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Tweet(models.Model):
	twitter_handle = models.CharField(max_length=16)
	picture_url = models.CharField(max_length=200)
	posting_date = models.DateTimeField()