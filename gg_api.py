#!/usr/bin/env python

"""gg_api.py: Parses tweets about an awards ceremony in order to determine
the nominees, winners, and presenters, as well as other points of interest
relating to the event.
"""
import json
import re
import sys
import time
from collections import Counter

import spacy
from spacy.tokenizer import Tokenizer
from imdb import IMDb

__author__ = "Michael Huyler, Robert Smart, Salome Wairimu, Ulyana Kurylo"

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

"""Awards Ceremony-specific parameters."""
AWARD_CEREMONY_TITLE = "Golden Globes"
MAX_NUM_HOSTS = 2
AWARD_TOKEN_SET = set()
AWARD_CERMONY_KEYWORDS = ["#", "goldenglobes", "golden", "globes"]
AWARD_CATEGORY_KEYWORDS = {"PERSON": ["actor", "actress", "director", "cecil"]}

MAX_TWEETS_PARSED = 10_000
ALL_TWEETS = {}
DEBUG = True

"""Private variables used for natural language processing."""
__nlp = spacy.load('en_core_web_sm')
__imdb = IMDb()
__tokenizer = Tokenizer(__nlp.vocab)


def get_hosts(year):
    """Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    host_tweets = []
    for tweet in ALL_TWEETS:
        if 'host' in tweet and 'next year' not in tweet:
            host_tweets.append(tweet)
    potential_hosts = __common_objects(host_tweets, 'PERSON')
    c = Counter(potential_hosts)
    hosts = []
    host_counts = c.most_common(MAX_NUM_HOSTS)
    max = host_counts[0][1]
    for potential_host in host_counts:
        if potential_host[1] > (0.15 * max):
            hosts.append(potential_host[0])
    print("HOSTS: " + str(hosts)) if DEBUG else 0
    return hosts


def get_awards(year):
    """Awards is a list of strings. Do NOT change the name
    of this function or what it returns.
    """
    # Your code here
    awards = []
    print("AWARDS: " + str(awards)) if DEBUG else 0
    return awards


def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.
    """
    # Your code here
    nominees = []
    print("NOMINEES: " + str(nominees)) if DEBUG else 0
    return nominees


def get_winner(year):
    """Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.
    """
    # Your code here
    winners = []
    for award in OFFICIAL_AWARDS:
        """Determine what category of objects wins an award. If the award title
        contains certain keywords, then it goes to a person, otherwise it should
        go to a movie/television series.
        """
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
    print("WINNERS: " + str(winners)) if DEBUG else 0
    return winners


def get_presenters(year):
    """Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.
    """
    # Your code here
    presenters = []
    print("PRESENTERS: " + str(presenters)) if DEBUG else 0
    return presenters


def __common_objects(tweets, type):
    """Performs natural language processing on tweets,
    and attempts to match tokens to people or works of art from IMDb
    """
    global ALL_TWEETS
    objects = {}
    for tweet in tweets:
        if ALL_TWEETS[tweet] is None:
            ALL_TWEETS[tweet] = __nlp(tweet).ents
        for ent in ALL_TWEETS[tweet]:
            if ent.label_ == type:
                if ent.text in objects:
                    objects[ent.text] += 1
                else:
                    imdb_matches = []
                    if type == 'PERSON':
                        imdb_matches = __imdb.search_person(ent.text)
                    elif type == 'WORK_OF_ART':
                        imdb_matches = __imdb.search_movie(ent.text)
                    if imdb_matches != []:
                        ents = __tokenizer(ent.text)
                        tokens = set()
                        for token in ents:
                            tokens.add(str(token).lower())
                        intersect = tokens.intersection(AWARD_TOKEN_SET)
                        if len(intersect) < int(len(tokens) / 2):
                            objects[ent.text] = 1
    return objects


def __create_output(type):
    output = ""
    if type == "human":
        pass
    elif type == "json":
        pass
    return output


def __load_input_corpus(filename):
    global ALL_TWEETS
    count = 0
    with open(filename, 'r') as corpus:
        jsonData = json.load(corpus)
        for item in jsonData:
            if (count > MAX_TWEETS_PARSED):
                break
            tweet = item.get("text")
            ALL_TWEETS[tweet] = None
            count += 1


def __create_token_set():
    for award in OFFICIAL_AWARDS:
        for token in __tokenizer(award):
            AWARD_TOKEN_SET.add(str(token))
    for keyword in AWARD_CERMONY_KEYWORDS:
        AWARD_TOKEN_SET.add(keyword)
    return


def pre_ceremony():
    """This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.
    """
    # Your code here
    # // TODO: "...stores that data in your DB or in a json [etc]..." \
    # I believe that means we don't need this function since we don't store \
    # any data, we need only parse the given json file when main() runs?
    print("Pre-ceremony processing complete.")
    return


def main():
    """This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.
    """
    # Your code here
    # TODO: Call pre_ceremony() ?
    jsonFile = sys.argv[1]
    pattern = re.compile("\d\d\d\d")
    year = pattern.search(jsonFile).group(0)

    timer = time.time()

    __load_input_corpus(jsonFile)
    __create_token_set()
    get_hosts(year)
    get_awards(year)
    get_nominees(year)
    get_winner(year)
    get_presenters(year)
    humanReadableOutput = __create_output("human")
    jsonOutput = __create_output("json")

    print(time.time() - timer)
    return


if __name__ == '__main__':
    main()
