import re
import json
# import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# from nltk.tokenize import word_tokenize
# from nltk.tag import pos_tag
import spacy
nlp = spacy.load('en_core_web_sm')
from imdb import IMDb
from collections import Counter
import pprint

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - musical or comedy', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
award_token_set = set()
for award in OFFICIAL_AWARDS:
    for token in nlp(award):
        award_token_set.add(str(token))
award_token_set.add("goldenglobes")
award_token_set.add("golden")
award_token_set.add("globes")
award_token_set.add("#")

official_award_tokens={}
award_mapping={}
for award in OFFICIAL_AWARDS:
    for token in nlp(award):
        if award in official_award_tokens:
            official_award_tokens[award].append(str(token))
        else:
            official_award_tokens[award]=[str(token)]
            award_mapping[award]=[award]

#print(award_tokens)


def get_tweets(year): 
    filename="gg"+year+".json"
    tweets = []
    with open(filename,'r') as corpus:
        jsonData=json.load(corpus)
        for item in jsonData:
            tweet = item.get("text")
            tweets.append(tweet)
    return tweets


all_tweets_2013 = get_tweets("2013")
#all_tweets_2015 = get_tweets("2015")


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
            if ent.label_ == type or type=='WORK_OF_ART':
                #pattern = re.compile("\w+\s\w+")
                # check if person's name matches standard naming
                #if pattern.fullmatch(ent.text):
                if ent.text in objects:
                    objects[ent.text] += 1
                else:
                    imdb_matches = []
                    if type == 'PERSON':
                        imdb_matches = imdb.search_person(ent.text)
                    else:
                        imdb_matches = imdb.search_movie(ent.text)
                    if imdb_matches != []:
                        #for award in OFFICIAL_AWARDS:
                        ents=nlp(ent.text)
                        #awards=nlp(award)
                        set1=set()
                        # set2=set()
                        for token in ents:
                            set1.add(str(token).lower())
                        inter=set1.intersection(award_token_set)
                        
                        if len(inter)<int(len(set1)/2):
                            #print(set1)
                            objects[ent.text] = 1
    return objects



def get_hosts(year):
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
    all_tweets=[]
    award_tweets=[]
    result=[]
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
    for key,value in awards_sorted:
        result.append(key)
        #print(str(a) + "\n")

    return result


our_2013_awards=get_awards('2013')

# def populate_awards_dictionary:
#     for award in our_2013_awards:
#         tokens=set()
#         for token in nlp(award):
#             tokens.add(str(token))
#         for official_award in official_award_tokens:
#             award_set=set(official_award_tokens[official_award])
#             if len(tokens.intersection(award_set))/len(tokens.union(award_set)):
#                 award_mapping[official_award].append(award)
#     return award_mapping

def __map_awards(unofficial_awards):
    matching_matrix=[[0 for j in range(len(OFFICIAL_AWARDS))] for i in range(len(unofficial_awards))]
    for i in range(len(unofficial_awards)):
        tokens=set()
        for token in nlp(unofficial_awards[i]):
            tokens.add(str(token))
        for j in range(len(OFFICIAL_AWARDS)):
            award_set=set(official_award_tokens[OFFICIAL_AWARDS[j]])
            matching_matrix[i][j]=len(tokens.intersection(award_set))
    
    for i in range(len(matching_matrix)):
        max_col_index=matching_matrix[i].index(max(matching_matrix[i]))
        if matching_matrix[i][max_col_index]>3:
            award_mapping[OFFICIAL_AWARDS[max_col_index]].append(unofficial_awards[i])

            
    return award_mapping

res=__map_awards(our_2013_awards)
#print(res)
#pprint.pprint(res)
# for key,value in res:
#     print(str(key)+" "+str(value)+"\n")

        




def GetWinners(year):
    all_tweets=[]
    if year=='2013':
        all_tweets=all_tweets_2013
    if year=='2015':
        all_tweets=all_tweets_2015


    for award in OFFICIAL_AWARDS:
        # if award needs a person as a result (actor/actress/director/etc)
        type_of_award = ""
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            type_of_award = "name"
        # reduce to tweets about the desired award and nominee
        #relevant_tweets = [tweet for tweet in all_tweets if award.lower() in tweet.lower()]
        relevant_tweets=[]
        for tweet in all_tweets:
            if 'RT' not in tweet:
                adder=False
                for match in award_mapping[award]:
                    if match.lower() in tweet.lower():
                        adder=True
                if adder:
                    relevant_tweets.append(tweet)
        winners = {}
        if (type_of_award == "name"):
            winners = CommonObjects(relevant_tweets, 'PERSON')
        else:
            winners = CommonObjects(relevant_tweets, 'WORK_OF_ART')
        c = Counter(winners)
        #print(winners)
        if (len(c.most_common(1)) > 0):
            winner = c.most_common(1)[0][0]
            print(award + "\t" + winner + "\n")
        else:
            print(award + ("\tMeryl Streep?\n" if type_of_award == "name" else "\tMy favorite movie?\n"))


GetWinners('2013')