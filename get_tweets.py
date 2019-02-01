import re
import json
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import spacy
from spacy.lang.en import English
nlp = spacy.load('en_core_web_sm')
from imdb import IMDb
from collections import Counter


def get_tweets_2013():
    tweets = []
    with open('gg2013.json','r') as corpus:
        jsonData=json.load(corpus)
        for item in jsonData:
            tweet = item.get("text")
            tweets.append(tweet)
    return tweets
def get_tweets_2015():
    tweets = []
    with open('gg2015.json','r') as corpus:
        jsonData=json.load(corpus)
        for item in jsonData:
            tweet = item.get("text")
            tweets.append(tweet)
    return tweets


#all_tweets_2013=get_tweets_2013()
all_tweets_2015=get_tweets_2015()

def get_hosts(year):
    all_tweets_2013=[]
    global all_tweets_2015
    all_tweets=[]
    host_tweets=[]
    people={}
    imdb=IMDb()
    if year=='2013':
        all_tweets=all_tweets_2013
    elif year=='2015':
        all_tweets=all_tweets_2015
    
    for t in all_tweets[0:5000]:
        if 'host' in t and 'RT' not in t and 'next year' not in t:
            host_tweets.append(t)
    for t in host_tweets:
        #use spacy to get tweets that have a person
        special=nlp(t)
        for ent in special.ents:
            if ent.label_=='PERSON':
                pattern=re.compile("\w+\s\w+")
                #check if person's name matches standard naming
                if pattern.fullmatch(ent.text):
                    if ent.text in people:
                        people[ent.text]+=1
                    else:
                        persons=imdb.search_person(ent.text)
                        if persons != []:
                            people[ent.text]=1
                           
    c = Counter(people)
    hosts=[]
    i=5
    host_counts=c.most_common(i)
    print(host_counts)
    for j in host_counts:
        hosts.append(j[0])
    return(hosts)



print(get_hosts('2015'))

def get_awards(year):
    awards_keywords={'best','motion','picture','supporting','performance','director','drama','musical','comedy','television','series','screenplay','original'}
    global all_tweets_2013
    global all_tweets_2015
    all_tweets=[]
    award_tweets=[]
    awards={}
    imdb=IMDb()
    if year=='2013':
        all_tweets=all_tweets_2013
    elif year=='2015':
        all_tweets=all_tweets_2015


#get_awards('2013')

