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

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - musical or comedy', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

nlp.Defaults.stop_words|={"by","an","a","in","for"}

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


def CommonObjects(tweets, type):
    """Performs natural language processing on tweets,
    and attempts to match tokens to people or works of art from IMDb
    """
    objects = {}
    imdb = IMDb()
    for t in tweets:
        # use spacy to get tweets that have a person
        special = nlp(t)
        for ent in special.ents:
            if ent.label_ == type:
                pattern = re.compile("\w+\s\w+")
                # check if person's name matches standard naming
                if pattern.fullmatch(ent.text):
                    if ent.text in objects:
                        objects[ent.text] += 1
                    else:
                        imdb_matches = []
                        if type == 'PERSON':
                            imdb_matches = imdb.search_person(ent.text)
                        else:
                            imdb_matches = imdb.search_movie(ent.text)
                        if imdb_matches != []:
                            print(imdb_matches)
                            objects[ent.text] = 1
    return objects


all_tweets_2013 = get_tweets_2013()
all_tweets_2015 = None #= get_tweets_2015()

def get_hosts(year):
    all_tweets_2013=[]
    global all_tweets_2015
    all_tweets=[]
    host_tweets=[]
    if year=='2013':
        all_tweets=all_tweets_2013
    elif year=='2015':
        all_tweets=all_tweets_2015

    for t in all_tweets[0:10000]:
        if 'host' in t and 'next year' not in t:
            host_tweets.append(t)

    people = CommonObjects(host_tweets, 'PERSON')
    c = Counter(people)
    hosts=[]
    i=2
    host_counts=c.most_common(i)
    highest_count=host_counts[0][1]
    for j in host_counts:
        if j[1]>(0.15*highest_count):
            hosts.append(j[0])
    return(hosts)


# print(get_hosts('2015'))


def get_awards(year):
    awards_keywords={'best','motion','picture','supporting','performance','director','drama','musical','comedy','television','series','screenplay','original'}
    global all_tweets_2013
    all_tweets_2015=[]
    all_tweets=[]
    award_tweets=[]
    awards={}
    imdb=IMDb()
    if year=='2013':
        all_tweets=all_tweets_2013
    elif year=='2015':
        all_tweets=all_tweets_2015

    pattern=re.compile("Best ([A-z\s-]+)[A-Z][a-z]*[^A-z]")
    award_tweets = [pattern.search(t).group(0)[:-1] for t in all_tweets if pattern.search(t)]# and "RT" not in t]
    pattern=re.compile(".*^((?!(goes|but|is)).)*$")
    award_tweets = [pattern.match(t).group(0).lower() for t in award_tweets if pattern.match(t)]
    tweet_dict = {}
    for tweet in award_tweets:
        if tweet in tweet_dict:
            tweet_dict[tweet] += 1
        else:
            tweet_dict[tweet] = 1
    awards_sorted = sorted(tweet_dict.items(), key=lambda tweet: tweet[1])
    for a in awards_sorted:
        print(str(a) + "\n\n")


    special=nlp("Best Performance Actress Motion Picture - Drama: Jessica Chastain for Zero Dark Thirty #GoldenGlobes")
    print([(X.text, X.label_) for X in special.ents])
    print(special)
    #print(award_tweets)


#get_awards('2013')

def GetWinners(year):
    global all_tweets_2013
    global all_tweets_2015
    all_tweets=[]
    if year=='2013':
        all_tweets=all_tweets_2013
    if year=='2015':
        all_tweets=all_tweets_2015

    print(spacy.explain("WORK_OF_ART"))

    for award in OFFICIAL_AWARDS:
        # if award needs a person as a result (actor/actress/director/etc)
        type_of_award = ""
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            type_of_award = "name"
        # reduce to tweets about the desired award and nominee
        relevant_tweets = [tweet for tweet in all_tweets if award.lower() in tweet.lower()]
        winners = {}
        if (type_of_award == "name"):
            winners = CommonObjects(relevant_tweets, 'PERSON')
        else:
            winners = CommonObjects(relevant_tweets, 'WORK_OF_ART')
        c = Counter(winners)
        if (len(c.most_common(1)) > 0):
            winner = c.most_common(1)[0][0]
            print(award + "\t" + winner + "\n")
        else:
            print(award + ("\tMeryl Streep?\n" if type_of_award == "name" else "\tMy favorite movie?\n"))


GetWinners('2013')