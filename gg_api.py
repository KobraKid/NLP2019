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

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
OFFICIAL_AWARDS = None

"""Awards Ceremony-specific parameters."""
AWARD_CEREMONY_TITLE = "Golden Globes"
MAX_NUM_HOSTS = 2
AWARD_TOKEN_SET = set()
AWARD_CERMONY_KEYWORDS = ["#", "goldenglobes", "golden", "globes", "#goldenglobes"]
AWARD_CATEGORY_KEYWORDS = {"PERSON": ["actor", "actress", "director", "cecil"]}

MAX_TWEETS_PARSED = 10_000
ALL_TWEETS = {}
IMDB_RESULTS = {}
DEBUG = True

"""A dictionary with official awards as keys and get_awards as values, employing tokenization"""
official_award_tokens = {}
award_mapping = {}


"""Private variables used for natural language processing."""
__nlp = spacy.load('en_core_web_sm')
__imdb = IMDb()
__tokenizer = Tokenizer(__nlp.vocab)
current_year = None


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
    potential_hosts = __common_objects(host_tweets[0:10000], 'PERSON')
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
    award_tweets = []

    pattern = re.compile("Best ([A-z\s-]+)[A-Z][a-z]*[^A-z]")
    award_tweets = [pattern.search(t).group(0)[:-1] for t in ALL_TWEETS if pattern.search(t)]
    pattern = re.compile(".*^((?!(goes|but|is)).)*$")
    award_tweets = [pattern.match(t).group(0).lower() for t in award_tweets if pattern.match(t)]
    tweet_dict = {}
    for tweet in award_tweets:
        if tweet in tweet_dict:
            tweet_dict[tweet] += 1
        else:
            tweet_dict[tweet] = 1
    awards_sorted = sorted(tweet_dict.items(), key=lambda tweet: tweet[1])
    for key, value in awards_sorted:
        awards.append(key)

    __map_awards(awards)
    print("AWARDS: " + str(awards)) if DEBUG else 0
    return awards


def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    nominees = {}

    for award in OFFICIAL_AWARDS:
        # if award needs a person as a result (actor/actress/director/etc)
        type_of_award = ""
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            type_of_award = "name"
        # reduce to tweets about the desired award and nominee
        relevant_tweets = []
        for tweet in ALL_TWEETS:
            if 'RT' not in tweet:
                adder = False
                for match in award_mapping[award]:
                    if match.lower() in tweet.lower():
                        adder = True
                if adder:
                    relevant_tweets.append(tweet)
        potential_nominees = {}
        if (type_of_award == "name"):
            potential_nominees = __common_objects(relevant_tweets, 'PERSON')
        else:
            potential_nominees = __common_objects(relevant_tweets, 'WORK_OF_ART')
        c = Counter(potential_nominees)
        if (len(c.most_common(1)) > 0):
            nominees[award] = [nom[0] for nom in c.most_common(5) if nom]
        else:
            print(award + ("\tMeryl Streep?\n" if type_of_award == "name" else "\tMy favorite movie?\n"))
    print("NOMINEES: " + str(nominees)) if DEBUG else 0
    return nominees


def get_winner(year):
    """Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    winners = {}

    for award in OFFICIAL_AWARDS:
        # if award needs a person as a result (actor/actress/director/etc)
        type_of_award = ""
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            type_of_award = "name"
        # reduce to tweets about the desired award and nominee
        relevant_tweets = []
        for tweet in ALL_TWEETS:
            if 'RT' not in tweet:
                adder = False
                for match in award_mapping[award]:
                    if match.lower() in tweet.lower():
                        adder = True
                if adder:
                    relevant_tweets.append(tweet)
        if (type_of_award == "name"):
            potential_winners = __common_objects(relevant_tweets, 'PERSON')
        else:
            potential_winners = __common_objects(relevant_tweets, 'WORK_OF_ART')
        c = Counter(potential_winners)
        if (len(c.most_common(1)) > 0):
            winner = c.most_common(1)[0][0]
            winners[award] = winner
        else:
            winners[award] = ("\tUnknown Person\n" if type_of_award == "name" else "\tUnknown Media\n")
    print("WINNERS: " + str(winners)) if DEBUG else 0
    return winners


def get_presenters(year):
    """Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS

    #reduce to the tweets that we care about, those about presenters
    relevant_tweets = [tweet for tweet in ALL_TWEETS if 'present' in tweet]

    for award in OFFICIAL_AWARDS:
        #further reduce tweets to be only those pertaining to the award in question
        award_tweets = []
        for tweet in relevant_tweets:
            adder = False
            for match in award_mapping[award]:
                if match.lower() in tweet.lower():
                    adder = True
            if adder:
                award_tweets.append(tweet)
        #find the most common person in the awards
        presenter_list = __common_objects(award_tweets, 'PERSON')
        c = Counter(presenter_list)
        if(len(c.most_common(1))>0):
            presenter=c.most_common(1)[0][0]
            print(award + '\t' + presenter + '\n')
        else:
            print(award + '\t' + 'idk' + '\n')



    presenters = {}
    for award in OFFICIAL_AWARDS:
        presenters[award] = ''
    print("PRESENTERS: " + str(presenters)) if DEBUG else 0
    return presenters


def __common_objects(tweets, type):
    """Performs natural language processing on tweets,
    and attempts to match tokens to people or works of art from IMDb
    """
    global ALL_TWEETS
    words = {}
    name_pattern = re.compile('[A-Z][a-z]*\s[\w]+')
    for tweet in tweets:
        if ALL_TWEETS[tweet] is None:
            ALL_TWEETS[tweet] = __nlp(tweet).ents
        for ent in ALL_TWEETS[tweet]:
            cleaned_entity = ent.text.strip()
            if type == 'PERSON' and name_pattern.match(cleaned_entity) is None:
                continue
            ents = __tokenizer(cleaned_entity)
            tokens = set()
            for token in ents:
                tokens.add(str(token).lower())
            intersect = tokens.intersection(AWARD_TOKEN_SET)
            if len(intersect) < int(len(tokens) / 2) or len(intersect) == 0:
                if cleaned_entity in words:
                    words[cleaned_entity] += 1
                else:
                    words[cleaned_entity] = 1
    return words


def __create_output(type):
    output = ""
    if type == "human":
        pass
    elif type == "json":
        pass
    return output


def __map_awards(unofficial_awards):
    global award_mapping

    for award in OFFICIAL_AWARDS:
        for token in __nlp(award):
            if award in official_award_tokens:
                official_award_tokens[award].append(str(token))
            else:
                official_award_tokens[award] = [str(token)]
                award_mapping[award] = [award]

    matching_matrix = [[0 for j in range(len(OFFICIAL_AWARDS))] for i in range(len(unofficial_awards))]
    for i in range(len(unofficial_awards)):
        tokens = set()
        for token in __nlp(unofficial_awards[i]):
            tokens.add(str(token))
        for j in range(len(OFFICIAL_AWARDS)):
            award_set = set(official_award_tokens[OFFICIAL_AWARDS[j]])
            matching_matrix[i][j] = len(tokens.intersection(award_set))

    for i in range(len(matching_matrix)):
        max_col_index = matching_matrix[i].index(max(matching_matrix[i]))
        if matching_matrix[i][max_col_index] > 3:
            award_mapping[OFFICIAL_AWARDS[max_col_index]].append(unofficial_awards[i])

    return award_mapping


def __load_input_corpus(filename):
    global ALL_TWEETS
    count = 0
    with open(filename, 'r') as corpus:
        jsonData = json.load(corpus)
        for item in jsonData:
            # if (count > MAX_TWEETS_PARSED):
            #     break
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


def __perform_all_gets(year):
    predicted_hosts = get_hosts(year)
    predicted_awards = get_awards(year)
    predicted_nominees = get_nominees(year)
    predicted_winners = get_winner(year)
    predicted_presenters = get_presenters(year)
    humanReadableOutput = __create_output("human")
    jsonOutput = __create_output("json")


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


def main(self, file=None):
    """This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.
    """
    # Your code here
    jsonFile = file
    if len(sys.argv) <= 1 and file is None:
        print("Warning, no JSON file specified. Defaulting to 2013.")
        jsonFile = 'gg2013.json'
    elif file is None:
        jsonFile = sys.argv[1]
    pattern = re.compile("\d\d\d\d")
    year = pattern.search(jsonFile).group(0)
    global current_year
    current_year = year

    # Get the right set of awards based on year
    global OFFICIAL_AWARDS
    if year == "2013" or year == "2015":
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315
    else:
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1819

    __load_input_corpus(jsonFile)
    __create_token_set()

    return


if __name__ == '__main__':
    # TIMER START
    timer = time.time()

    main(None)
    __perform_all_gets(current_year)

    # TIMER END
    print(time.time() - timer)
