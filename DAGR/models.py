from __future__ import unicode_literals

from django.db import models

# Create your models here.

class DAGR(models.Model):
	GUID = models.CharField(pk=True)
	size = models.BigIntegerField(blank=True) # blank=true for tweets and websites
	file_name = models.CharField(max_length=200, blank=True)
	annotated_name = models.CharField(max_length=200)
	SHA1 = models.CharField(max_length=200. blank=True)
	creation_date = models.DateTimeField()
	local_path = models.CharField(max_length=200, blank=True)

class Relationship(models.Model):
	parent_GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	child_GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)

class Webpage(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	url = models.CharField(max_length=200)
	title = models.CharField(max_length=200, blank=True)

class Word_Document(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	page_count = models.IntegerField()
	word_count = models.IntegerField()
	paragraph_count = models.IntegerField()
	author = models.CharField(max_length=200)
	date_modified = models.DateTimeField()

class Keyword(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	keyword = models.CharField(max_length=200)

class Image(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	image_width = models.IntegerField()
	image_height = models.IntegerField()

class Audio(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	title = models.CharField(max_length=200, null=True)
	artist = models.CharField(max_length=200, null=True)
	year = models.IntegerField(null=True)
	composer = models.CharField(max_length=200, null=True)
	track = models.IntegerField(null=True)
	album = models.CharField(max_length=200, null=True)

class Video(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	video_width = models.IntegerField()
	video_height = models.IntegerField()

class Tweet(models.Model):
	tweet_types = (
		('T', 'Tweet'),
		('R', 'Reply'),
		('RT', 'Retweet')
	)
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	tweet_id = models.CharField(max_length=200)
	twitter_handle = models.CharField(max_length=16)
	tweet_type = models.CharField(max_length = 2, choices = tweet_types)
	likes = models.IntegerField()
	retweets = models.IntegerField()
	