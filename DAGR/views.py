from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import urllib2

from DAGR.models import *
from .forms import UploadFileForm

import oauth2
import json
from datetime import datetime

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_SECRET = settings.ACCESS_SECRET
# Create your views here.

@csrf_exempt
def meta(request):
    if request.method == "POST":
        data = json.loads(request.body)
        for meta in data['data']:
            guid = get_GUID()
            file_name = meta['file_name']
            path = meta['localpath']
            a_name = meta['a_name']
            table = meta['table']
            size = meta['size']
            creation_date = datetime.now()

            dagr = DAGR.objects.create(
                GUID = guid,
                size = size,
                annotated_name = a_name,
                creation_date =  creation_date,
                file_name = file_name,
                local_path = path,
                datatype = meta['type']
            )
            if table == 'img':
                Image.objects.create(
                    GUID = dagr,
                    image_width = meta['width'],
                    image_height = meta['height']
                )
            elif table == 'vid':
                Video.objects.create(
                    GUID = dagr,
                    video_width = meta['width'],
                    video_height = meta['height'],
                    duration = meta['duration']
                )
            elif table == 'audio':
                if 'composer' in meta:
                    composer = meta['composer']
                else:
                    composer = None
                if 'track_num' in meta:
                    track_num = meta['track_num']
                else:
                    track_num = None
                if 'album' in meta:
                    album = meta['album']
                else:
                    album = None
                if 'genre' in meta:
                    genre = meta['genre']
                else:
                    genre = None

                Audio.objects.create(
                    GUID = dagr,
                    duration = meta['duration'],
                    title = meta['title'],
                    genre = genre,
                    composer = composer,
                    track = track_num,
                    album = album,
                )
            elif table == 'doc':
                Word_Document.objects.create(
                    GUID = dagr,
                    char_count = meta['char_count'],
                    word_count = meta['word_count'],
                    author = meta['author'],
                    date_created = meta['created'],
                    date_modified = meta['modified']
                )


        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("not a post request")

def test(request):
    if request.method == "POST":
        if request.FILES and request.POST:
            a = []
            for file in request.FILES["files"]:
                
                a.append([type(file).__name__])

            if request.POST["annotated_name"] and request.POST['keywords']:
                context = {
                    "name" : 0,
                    "key" : 0,
                    "a" : a
                }
                context['name'] = request.POST["annotated_name"]
                context['key'] = request.POST['keywords']
            else:
                context = {
                    'error' : "Form was invalid, please try again filling out appropriate fields"
                }
                return render(request, 'DAGR/addfile.html', context)



            return HttpResponse(json.dumps(context), content_type='application/json')
        return HttpResponse(request.POST)
    context = {}
    return render(request, 'DAGR/addfile.html', context)

def home(request):
    # If the form was submitted
    if request.method == "POST":
        # First check if the user exists
        handle = request.POST['handle']
        num_tweets = request.POST['quantity']

        url = 'https://api.twitter.com/1.1/users/lookup.json?screen_name='+handle

        user_exist_respnse = oauth_req(url, CONSUMER_KEY, CONSUMER_SECRET)
        data = json.loads(user_exist_response)

        if not isinstance(data, list):
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?tweet_mode=extended'+'&screen_name='+handle+'&count='+num_tweets
            timeline_response = oauth_req(url, CONSUMER_KEY, CONSUMER_SECRET)
            data = json.loads(timeline_response)

            tweet_list = []

            for tweet in data:
                # if there is media then we want to add this to our database
                # we will add every tweet with a picture to our database
                tweet_id = tweet['id_str']
                if Tweet.objects.filter(tweet_id=tweet_id).count() == 0:
                    twitter_handle = handle
                    retweets = tweet['retweet_count']
                    likes = tweet['favorite_count']
                    tweet_type = ""
                    if tweet['in_reply_to_status_id']:
                        tweet_type = "R"
                    elif tweet[retweeted_status]:
                        tweet_type = "RT"
                    else:
                        tweet_type = "T"
                    ts = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                    if 'media' in tweet['entities']:
	                    # IN HERE GET ALL DIFFERENT MEDIAS AND CREATE DATABASE OBJECTS
	                    media_url = tweet['entities']['media'][0]['media_url']
                    new_GUID = get_GUID()
                    dagr = DAGR.objects.create(
		        		GUID = new_GUID,
		        		size = 0,
		        		annotated_name = tweet_id,
		        		creation_date =  datetime.datetime.now(),
                        datatype = "tweet"
	        		)
                    tweet_list.append(
                	    Tweet(
                            twitter_handle= twitter_handle,
                            tweet_type = tweet_type,
                            likes = likes,
                            posting_date=ts,
                            GUID = dagr,
                            retweets = retweets,
                    	)

                    )

            Tweet.objects.bulk_create(tweet_list)
            context = {
                "success" : str(len(tweet_list))+" "+"Tweets Have Been Added",
            }
            return render(request, 'DAGR/home.html', context)


    context = {}
    return render(request, 'DAGR/home.html', context)

def get_GUID():
	response = urllib2.urlopen('http://setgetgo.com/guid/get.php')
	return response.read()

def oauth_req(url, key, secret):
        consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
        access_token = oauth2.Token(key=ACCESS_TOKEN, secret=ACCESS_SECRET)
        client = oauth2.Client(consumer, access_token)
        resp, content = client.request(url)
        return content

def gallery(request):
    all_tweets = Tweet.objects.all()
    context = {
        'tweets' : all_tweets
    }
    return render(request, 'use_twitter/gallery.html', context)

"""
These 4 will require Hachoir/other parsing methods to get metadata


def create_Image(GUID):
	new_Image = Image.objects.create(
		GUID= GUID,
		image_width = 0 , #change to whatever hachoir extracts
		image_height = 0,
		)

def create_Video(GUID):
	new_Video = Video.objects.create(
		GUID= GUID,
		video_width = 0 , #change to whatever hachoir extracts
		video_height = 0,
		)

def create_Audio(GUID):
	new_Audio = Audio.objects.create(
		GUID = GUID,
		title = "",
		artist = "",
		year = 0,
		composer = "".
		track = 0,
		album = "",
	)

def create_Word_Document(GUID):
	new_Doc = Word_Document.objects.create(
		GUID = GUID,
		page_count = 0,
		word_count = 0,
		paragraph_count = 0,
		author = "",
		date_modified = datetime.datetime.now()
	)

"""

"""
def create_Webpage(GUID):


"""