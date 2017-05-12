from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from bs4 import BeautifulSoup
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
            for keyword in meta['keywords']:
                if Keyword.objects.filter(keyword=keyword).count()==0:
                    new_key = Keyword(keyword=keyword)
                    
                    new_key.save()
                    new_key.dagr.add(dagr)
                else:
                    key = Keyword.objects.get(keyword=keyword)

                    key.dagr.add(dagr)
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

def add_website(request):
    if request.method == 'POST':
        return HttpResponse('working')
    return render(request, 'DAGR/addweb.html', {})

def details(request, GUID):
    objects = []

    dagr = DAGR.objects.get(GUID=GUID) 
    web = (Webpage.objects.filter(GUID=dagr).first())
    img =(Image.objects.filter(GUID=dagr).first())
    vid = (Video.objects.filter(GUID=dagr).first())
    audio = (Audio.objects.filter(GUID=dagr).first())
    tweet = (Tweet.objects.filter(GUID=dagr).first())
    doc = (Word_Document.objects.filter(GUID=dagr).first())
    objects.extend([dagr, web, img, vid, audio, tweet, doc])
    for obj in objects:
        if obj:
            obj.fields = dict(((field.name).upper, field.value_to_string(obj)) 
                    for field in obj._meta.fields if not field.primary_key)
    

    keywords = dagr.keyword_set.all()
    children = []
    qs = Relationship.objects.filter(parent_GUID = dagr)
    for q in qs:
        children.append(q.child_GUID)
    parents = []
    qs = Relationship.objects.filter(child_GUID = dagr)
    for q in qs:
        parents.append(q.parent_GUID)

    context = {
        'objects': objects,
        'children' : children,
        'parents' : parents,
        'keywords' : keywords,
        'dagr' : dagr

    }
    return render(request, 'DAGR/detail.html', context)

def time(request):
    if request.method =="POST":
        start_date = request.POST['start']
        end_date = request.POST['end']
        if start_date and end_date:
            qs = DAGR.objects.filter(creation_date__range=(start_date, end_date))
            return render(request, 'DAGR/time.html', {'result' : qs})
        else:
            return render(request, "DAGR/time.html", {'error' : "Invalid search input"})

    return render(request, 'DAGR/time.html', {})

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
    return render(request, 'DAGR/homepage.html', {})


def query(request):
    if request.method == 'POST':
        d = dict(request.POST)
        if request.POST['type'] == 'keyword':
            k = request.POST['params']
            if Keyword.objects.filter(keyword=k).count() == 0:
                return render(request, 'DAGR/query.html', {'error' : 'No DAGRs With Keyword ' + k +' Found'})
            else:
                keyword = Keyword.objects.get(keyword=k)
                dagrs = keyword.dagr.all()  
                return render(request, 'DAGR/query.html', {'error' : 'success', 'result':dagrs})

        elif request.POST['type'] == 'aname':
            k = request.POST['params']
            qs = DAGR.objects.filter(annotated_name__contains=k)
            if qs.count() == 0:
                return render(request, 'DAGR/query.html', {'error' : 'No DAGRs With Annotated Name ' + k +' Found'})
            else:
                return render(request, 'DAGR/query.html', {'error' : 'success', 'result':qs})
        elif request.POST['type'] == 'name':
            k = request.POST['params']
            qs = DAGR.objects.filter(file_name__contains=k)
            if qs.count() == 0:
                return render(request, 'DAGR/query.html', {'error' : 'No DAGRs With File Name ' + k +' Found'})
            else:
                return render(request, 'DAGR/query.html', {'error' : 'success', 'result':qs})

        elif request.POST['type'] == 'size':
            k = request.POST['params'].split(" ")
            min = k[0]
            max = k[1]
            if max < min:
                return render(request, 'DAGR/query.html', {'error' : 'max size must be less than minimum size'})
            else:
                qs = DAGR.objects.filter(size__gte=min, size__lte=max)
                if qs.count()==0:
                    msg = "No DAGRs with size >= " + str(min) + " and <= " + str(max) + " were found."
                    return render(request, 'DAGR/query.html', {'error' : msg})
                else:
                    return render(request, 'DAGR/query.html', {'error' : 'success', 'result':qs})


        elif request.POST['type'] == 'type':   
            k = request.POST['params']
            qs = DAGR.objects.filter(datatype__contains=k)
            if qs.count() == 0:
                return render(request, 'DAGR/query.html', {'error' : 'No DAGRs With Datatype ' + k +' Found'})
            else:
                return render(request, 'DAGR/query.html', {'error' : 'success', 'result':qs})

        return HttpResponse(json.dumps(d), content_type='application/json')
    return render(request, 'DAGR/query.html', {})



def orphan(request):
    qs = DAGR.objects.all()
    orphans = []
    for q in qs:
        if Relationship.objects.filter(child_GUID=q).count()==0:
            orphans.append(q)

    return render(request, 'DAGR/orphan.html', {'result' : orphans})
    

def sterile(request):
    qs = DAGR.objects.all()
    sterile = []
    for q in qs:
        if Relationship.objects.filter(parent_GUID=q).count()==0:
            sterile.append(q)

    return render(request, 'DAGR/sterile.html', {'result' : sterile})


def reach(request):
    if request.method == "POST":
        guid = request.POST['guid']
        if DAGR.objects.filter(GUID = guid).count() == 0:
            msg = "No DAGR with GUID: " + guid 
            return render(request, 'DAGR/reach.html', {"error" : msg})
        else:
            dagr = DAGR.objects.get(GUID=guid)

            context = get_reach(dagr)
            return render(request, "DAGR/reach.html", context)



    return render(request, 'DAGR/reach.html', {})



def delete(request, GUID):
    if request.method == "POST" and GUID:
        dagr = DAGR.objects.get(GUID=GUID)
        dagr.delete()
        context = {
            "msg" : "DAGR Successfully Deleted"
        }
        return redirect('query')
    context = get_reach(DAGR.objects.get(GUID=GUID))
    return render(request, 'DAGR/delete.html', context)

def edit(request, GUID):
    dagr = DAGR.objects.get(GUID=GUID)
    if request.method == "POST":
        parent_err = None
        child_err = None
        changed = None
        if request.POST['a_name']:
            if dagr.annotated_name != request.POST['a_name']:
                dagr.annotated_name = request.POST['a_name']
                dagr.save()
                changed = "Annotated Name Updated!"
        if 'add_parent' in request.POST and request.POST['add_parent'] != "":
            new_parent = DAGR.objects.filter(GUID=request.POST['add_parent']).first()
            if new_parent:
                Relationship.objects.create(parent_GUID=new_parent, child_GUID=dagr)
                parent_err = "A New Parent has been added to this DAGR"
            else:
                parent_err = "Parent GUID is Invalid, Relationship creation failed"
        if 'add_child' in request.POST and request.POST['add_child'] != "":
            new_child = DAGR.objects.filter(GUID=request.POST['add_child']).first()
            if new_child:
                Relationship.objects.create(parent_GUID=dagr, child_GUID=new_child)
                child_err = "A New Child has been added to this DAGR"
            else:
                child_err = "Child GUID is Invalid, Relationship creation failed"
        context = {
            'dagr' : dagr,
            'p_err' : parent_err,
            'c_err' : child_err,
            'changed' : changed,
            "a_n" : dagr.annotated_name
        }
        return render(request, 'DAGR/edit.html', context)
    context = {
        'dagr' : dagr,
        "a_n" : dagr.annotated_name   
    }
    return render(request, 'DAGR/edit.html', context)


def twitter(request):
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
	return response.read()[1:-1]

def oauth_req(url, key, secret):
        consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
        access_token = oauth2.Token(key=ACCESS_TOKEN, secret=ACCESS_SECRET)
        client = oauth2.Client(consumer, access_token)
        resp, content = client.request(url)
        return content

def get_reach(dagr):
    children = []
    qs = Relationship.objects.filter(parent_GUID = dagr)
    for q in qs:
        children.append(q.child_GUID)
    parents = []
    qs = Relationship.objects.filter(child_GUID = dagr)
    for q in qs:
        parents.append(q.parent_GUID)
    return {'children' : children,'parents' : parents,'guid' : dagr.GUID}