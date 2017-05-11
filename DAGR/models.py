from __future__ import unicode_literals

from django.db import models

# Create your models here.

class DAGR(models.Model):
	GUID = models.CharField(max_length = 200, primary_key=True)
	size = models.BigIntegerField(blank=True) # blank=true for tweets and websites
	file_name = models.CharField(max_length=200, blank=True)
	annotated_name = models.CharField(max_length=200)
	creation_date = models.DateTimeField()
	local_path = models.CharField(max_length=200, blank=True)
	datatype = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return self.GUID

class Relationship(models.Model):
	parent_GUID = models.ForeignKey(DAGR, related_name = 'parent', on_delete=models.CASCADE)
	child_GUID = models.ForeignKey(DAGR, related_name = 'child', on_delete=models.CASCADE)

class Webpage(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	url = models.CharField(max_length=200)
	title = models.CharField(max_length=200, blank=True)

class Word_Document(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	char_count = models.IntegerField()
	word_count = models.IntegerField()
	author = models.CharField(max_length=200)
	date_created = models.CharField(max_length=200)
	date_modified = models.CharField(max_length=200)

class Keyword(models.Model):

	dagr = models.ManyToManyField(DAGR)
	keyword = models.CharField(max_length=200)

class Image(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	image_width = models.IntegerField()
	image_height = models.IntegerField()

class Audio(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	title = models.CharField(max_length=200, null=True)
	genre = models.CharField(max_length=200, null=True)
	composer = models.CharField(max_length=200, null=True)
	track = models.IntegerField(null=True)
	album = models.CharField(max_length=200, null=True)
	duration = models.CharField(max_length=200)

class Video(models.Model):
	GUID = models.ForeignKey(DAGR, on_delete=models.CASCADE)
	duration = models.CharField(max_length=200)
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
