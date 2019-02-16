#!/usr/bin/env python

"""gg_api.py: Parses tweets about an awards ceremony in order to determine
the nominees, winners, and presenters, as well as other points of interest
relating to the event.
"""
import json
import math
import re
import statistics
import sys
import time
import gzip
import urllib.request
from collections import Counter
from difflib import SequenceMatcher

import spacy
from imdb import IMDb
from spacy.tokenizer import Tokenizer

__author__ = "Michael Huyler, Robert Smart, Salome Wairimu, Ulyana Kurylo"

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
OFFICIAL_AWARDS = None

"""Awards Ceremony-specific parameters."""
AWARD_CEREMONY_TITLE = "Golden Globes"
AWARD_TOKEN_SET = set()
AWARD_CERMONY_KEYWORDS = ["#", "goldenglobes", "golden", "globes", "#goldenglobes"]
AWARD_CATEGORY_KEYWORDS = {"PERSON": ["actor", "actress", "director", "cecil"]}

MAX_TWEETS_PARSED = 250_000
ALL_TWEETS = {}
IMDB_RESULTS = {}
DEBUG = False

"""A dictionary with official awards as keys and get_awards as values, employing tokenization"""
official_award_tokens = {}
award_mapping = {}

"""Private lists to store our results"""
__predicted_hosts = {}
__predicted_awards = {}
__predicted_nominees = {}
__predicted_winners = {}
__predicted_presenters = {}

"""Private variables used for natural language processing."""
__nlp = spacy.load('en_core_web_sm')
__imdb = IMDb()
__tokenizer = Tokenizer(__nlp.vocab)
current_year = None
__sentiment = {}


"""Begin Custom Functions"""


def __best_dressed(year):
    global ALL_TWEETS
    stopwords = ["Golden Globes", "@GoldenGlobes", "#goldenglobes", "Hollywood"]
    keywords = [
        "beautiful", "great outfit", "best dress", "amazing dress",
        "great suit", "gorgeous", "looks amazing"
    ]
    result = []
    relevant_tweets = []
    for tweet in ALL_TWEETS:
        if any(word in tweet for word in keywords):
            relevant_tweets.append(tweet)
    best_dressed_people = __common_objects(relevant_tweets, 'PERSON')
    cleaned_dict = {}
    for person in best_dressed_people:
        if person in stopwords:
            continue
        k = __val_exists_in_keys(cleaned_dict, person)
        if k is None:
            cleaned_dict[person] = best_dressed_people[person]
        else:
            cleaned_dict[k] += best_dressed_people[person]
    c = Counter(best_dressed_people)
    if (len(c.most_common(1)) > 0):
        result = [person[0] for person in c.most_common(5) if person]
    else:
        print("no none was best dressed")
    return result


def __worst_dressed(year):
    global ALL_TWEETS
    stopwords = ["Golden Globes", "@GoldenGlobes", "#goldenglobes", "Hollywood"]
    keywords = [
        "worst outfit", "bad outfit", "worst attire", "looks ugly",
        "bad attire", "gross", "ugly", "ugly dress", "ugly suit"
    ]
    result = []
    relevant_tweets = []
    for tweet in ALL_TWEETS:
        if any(word in tweet for word in keywords):
            relevant_tweets.append(tweet)
    worst_dressed_people = most_common(relevant_tweets, 'PERSON')
    cleaned_dict = {}
    for person in worst_dressed_people:
        if person in stopwords:
            continue
        k = __val_exists_in_keys(cleaned_dict, person)
        if k is None:
            cleaned_dict[person] = worst_dressed_people[person]
        else:
            cleaned_dict[k] += worst_dressed_people[person]

    c = Counter(cleaned_dict)
    if (len(c.most_common(1)) > 0):
        result = [person[0] for person in c.most_common(5) if person]
    else:
        print("no none was badly dressed")
    return result


"""Begin API Functions"""


def get_hosts(year):
    """Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    global __predicted_hosts
    host_tweets = []
    for tweet in ALL_TWEETS:
        if 'host' in tweet and 'next year' not in tweet:
            host_tweets.append(tweet)
    potential_hosts = __common_objects(host_tweets, 'PERSON')
    c = Counter(potential_hosts)
    hosts = []
    host_counts = c.most_common(len(c))
    max = host_counts[0][1]
    for potential_host in host_counts:
        if potential_host[1] > (0.25 * max):
            hosts.append(potential_host[0])
    print("HOSTS: " + str(hosts)) if DEBUG else 0
    __predicted_hosts = hosts
    return hosts


def get_awards(year):
    """Awards is a list of strings. Do NOT change the name
    of this function or what it returns.
    """
    # Your code here
    global __predicted_awards
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
    unofficial_awards = []
    avg = sum([v for k, v in awards_sorted]) / len(awards_sorted)
    std = statistics.stdev([v for k, v in awards_sorted])
    for key, value in awards_sorted:
        unofficial_awards.append(key)
        if value > math.floor(avg + (2 * std)):
            awards.append(key)
    __map_awards(unofficial_awards)
    print("AWARDS: " + str(awards)) if DEBUG else 0
    __predicted_awards = awards
    return awards


def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    global __predicted_nominees
    nominees = {}
    stopwords = ['winner', 'this year', 'tonight', 'next year\'s', 'next year', 'http', '@']
    stopword = stopwords + AWARD_CERMONY_KEYWORDS
    for award in OFFICIAL_AWARDS:
        # if award needs a person as a result (actor/actress/director/etc)
        type_of_award = ""
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            type_of_award = "name"
        # reduce to tweets about the desired award
        relevant_tweets = []
        for tweet in ALL_TWEETS:
            if not tweet.startswith('RT'):
                adder = False
                for match in award_mapping[award]:
                    if match.lower() in tweet.lower() or match.lower()[0:int(len(match.lower()) / 2)] in tweet.lower():
                        adder = True
                if adder:
                    relevant_tweets.append(tweet)
        print(relevant_tweets)
        potential_nominees = {}
        uncleaned_dict = {}
        if (type_of_award == "name"):
            uncleaned_dict = __common_objects(relevant_tweets, 'PERSON')
        else:
            uncleaned_dict = __common_objects(relevant_tweets, 'WORK_OF_ART')
        print(uncleaned_dict)
        for item in uncleaned_dict:
            adding = True
            for word in stopwords:
                if __is_similar(word, item.lower()) > 0.75 or item.lower() in word or word in item.lower():
                    adding = False
            if adding:
                k = __val_exists_in_keys(potential_nominees, item)
                if k is None:
                    potential_nominees[item] = uncleaned_dict[item]
                else:
                    potential_nominees[k] += uncleaned_dict[item]
        c = Counter(potential_nominees)
        # TODO: Don't cap nominees at 5, this is hardcoding and is bad
        if (len(c.most_common(1)) > 0):
            nominees[award] = [nom[0] for nom in c.most_common(5) if nom]
        else:
            nominees[award] = ["_nom_"]
    print("NOMINEES: " + str(nominees)) if DEBUG else 0
    __predicted_nominees = nominees
    return nominees


def get_winner(year):
    """Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    global __predicted_winners
    winners = {}
    for award in OFFICIAL_AWARDS:
        winners[award] = __predicted_nominees[award][0]
    print("WINNERS: " + str(winners)) if DEBUG else 0
    __predicted_winners = winners
    return winners


def get_presenters(year):
    """Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.
    """
    # Your code here
    global ALL_TWEETS
    global __predicted_presenters
    presenters = {}

    # Reduce to the tweets that we care about, those about presenters
    # relevant_tweets = [tweet for tweet in ALL_TWEETS if 'present' in tweet]
    relevant_tweets = [tweet for tweet in ALL_TWEETS]
    presenter_pattern = re.compile('present[^a][\w]*\s([\w]+\s){1,5}')

    for award in OFFICIAL_AWARDS:
        award_tweets = []
        for tweet in relevant_tweets:
            for a in award_mapping[award]:
                match = None
                # Reduce tweets to those pertaining to the award in question
                if a.lower() in tweet.lower():
                    match = presenter_pattern.search(tweet)
                # Reduce tweets to those pertaining to the winner of an award
                try:
                    contains_winner = __predicted_nominees[award][0].lower() in tweet.lower()
                    if contains_winner:
                        match = presenter_pattern.search(tweet)
                except KeyError:
                    pass
                if match:
                    award_tweets.append(tweet[0:match.span()[1]])
        # Find the most common person in the awards
        presenter_list = __process_presenters(award_tweets, award, __predicted_nominees)
        c = Counter(presenter_list)
        if len(c.most_common(1)) > 0:
            # TODO: Find the most common ones algorithmically, rather than with magic number
            presenters[award] = [pres[0] for pres in c.most_common(2) if pres]
        else:
            presenters[award] = ['_pre_']

    print("PRESENTERS: " + str(presenters)) if DEBUG else 0
    __predicted_presenters = presenters
    return presenters


def __is_similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def __val_exists_in_keys(keys_list, val):
    for key in keys_list:
        if __is_similar(key.lower(), val.lower()) >= 0.6 or val.lower() in key.lower() or key.lower() in val.lower():
            return key
    return None


def __common_objects(tweets, type):
    """Performs natural language processing on tweets,
    and attempts to match tokens to people or works of art from IMDb
    """
    stopwords = ['this year', 'tonight']
    global ALL_TWEETS
    words = {}
    name_pattern = re.compile('[A-Z][a-z]*\s[\w]+')
    for tweet in tweets:
        if ALL_TWEETS[tweet] is None:
            ALL_TWEETS[tweet] = __nlp(tweet).ents
        for ent in ALL_TWEETS[tweet]:
            if ent.label_ in ['NORP', 'ORDINAL', 'CARDINAL', 'QUANTITY', 'MONEY', 'DATE', 'TIME']:
                continue
            cleaned_entity = ent.text.strip()
            if cleaned_entity.lower() in stopwords:
                continue
            if type == 'PERSON' and name_pattern.match(cleaned_entity) is None:
                continue
            if (type == 'PERSON' and ent.label_ == 'PERSON') or type == 'WORK_OF_ART':
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


def __process_presenters(tweets, award, winners):
    global ALL_TWEETS
    words = {}
    for tweet in tweets:
        for ent in __nlp(tweet).ents:
            cleaned_entity = ent.text.strip()
            if str(cleaned_entity).lower().startswith("rt"):
                continue
            if str(cleaned_entity).lower() in winners[award][0].lower():
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


def __create_output(type, h=[], a={}, n={}, w={}, p={}):
    output = None
    if type == "human":
        output = ""
        # Host(s)
        output += "Host" + ("s: " if len(h) > 1 else ": ")
        for host in h:
            output += host + ", "
        output = output[:-2] + "\n\n"
        # Awards
        for i in range(len(OFFICIAL_AWARDS)):
            award = OFFICIAL_AWARDS[i]
            output += "Award: " + award + "\n"
            output += "Presenters: " + ''.join([(str(pres) + ", ") for pres in p[award]])
            output = output[:-2] + "\n"
            output += "Nominees: " + ''.join([(str(nom) + ", ") for nom in n[award]])
            output = output[:-2] + "\n"
            output += "Winner: " + w[award] + "\n\n"
    elif type == "json":
        data = {}
        data["hosts"] = h
        data["award_data"] = {}
        for i in range(len(OFFICIAL_AWARDS)):
            award = OFFICIAL_AWARDS[i]
            data["award_data"][award] = {
                "presenters": p[award],
                "nominees": n[award],
                "winner": w[award]
            }
        output = data
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
    with open(filename, 'r') as corpus:
        jsonData = json.load(corpus)
        for item in jsonData:
            tweet = item.get("text")
            ALL_TWEETS[tweet] = None
            __sentiment[tweet] = None
            if len(ALL_TWEETS) > MAX_TWEETS_PARSED:
                break


def __create_token_set():
    for award in OFFICIAL_AWARDS:
        for token in __tokenizer(award):
            AWARD_TOKEN_SET.add(str(token))
    for keyword in AWARD_CERMONY_KEYWORDS:
        AWARD_TOKEN_SET.add(keyword)
    return


def __perform_all_gets(year):
    get_hosts(year)
    get_awards(year)
    get_nominees(year)
    get_winner(year)
    get_presenters(year)
    human_readable_output = __create_output("human",
                                            __predicted_hosts,
                                            __predicted_awards,
                                            __predicted_nominees,
                                            __predicted_winners,
                                            __predicted_presenters)
    json_output = __create_output("json",
                                  __predicted_hosts,
                                  __predicted_awards,
                                  __predicted_nominees,
                                  __predicted_winners,
                                  __predicted_presenters)
    with open('data' + str(year) + '.json', 'w') as data:
        json.dump(json_output, data)
    print(human_readable_output)


def pre_ceremony():
    """This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.
    """
    # Your code here

    # download information from IMDB about movies and names
    # urllib.request.urlretrieve('https://datasets.imdbws.com/title.basics.tsv.gz', 'title.basics.tsv.gz')
    urllib.request.urlretrieve('https://datasets.imdbws.com/name.basics.tsv.gz', 'name.basics.tsv.gz')

    '''   # open the movies, names and process them
    f = gzip.open('title.basics.tsv.gz')
    movie_content = str(f.read())
    movie_lines = movie_content.split('\\n')
    movie_fields = []
    for line in movie_lines:
        movie_fields.append(line.split('\\t'))'''

    f = gzip.open('name.basics.tsv.gz')
    name_content = str(f.read())
    name_lines = name_content.split('\\n')
    name_fields = []
    for line in name_lines:
        name_fields.append(line.split('\\t'))

    '''    # arrange the movies by year, only caring about 2010 on
    movie_dict = {}
    for year in range(2010, 2020):
        movie_dict[str(year)] = []

    # ignore the first and last line
    for movie in movie_fields[1:len(movie_fields)-1]:
        # get the title, start year, and end year
        movie_name = movie[2]
        movie_start = movie[5]
        movie_end = movie[6]

        # if we're missing data, continue
        if movie_start == '\\\\N':
            continue

        # check if it's a movie or a tv show (which might exist for multiple years)
        if movie_end == '\\\\N':
            years_active = [int(movie_start)]
        else:
            years_active = range(int(movie_start), int(movie_end) + 1)

        # make sure that movie_end not before movie_start. If it is, continue
        if years_active == range(1,1):
            continue

        # check endpoints
        if years_active[0] < 2010 and years_active[-1] < 2010:
            continue

        if years_active[-1] > 2019:
            continue

        if years_active[0] < 2010:
            years_active = range(2010, years_active[-1]+1)

        for year in years_active:
            movie_dict[str(year)].append(movie_name)

    # save the dictionary to a json
    with open('movieyears.json', 'w') as f:
        json.dump(movie_dict, f)'''

    # do the same thing for names
    name_dict = {}
    for year in range(2010, 2020):
        name_dict[str(year)] = []

    # ignore the first and last line
    for name in name_fields[1:len(name_fields)-1]:
        # get the name, birth date, and death date
        name_name = name[1]
        name_birth = name[2]
        name_death = name[3]

        # if we're missing data, continue
        if name_birth == '\\\\N':
            continue

        # check if they're still alive
        if name_death == '\\\\N':
            years_active = range(int(name_birth), 2020)
        else:
            years_active = range(int(name_birth), int(name_death) + 1)

        # check that they weren't born before they died
        if years_active == range(1, 1):
            continue

        # check endpoints
        if years_active[0] < 2010 and years_active[-1] < 2010:
            continue

        if years_active[-1] > 2019:
            continue

        if years_active[0] < 2010:
            years_active = range(2010, years_active[-1]+1)

        for year in years_active:
            name_dict[str(year)].append(name_name)

    # save the dictionary to a json
    with open('nameyears.json', 'w') as f:
        json.dump(name_dict, f)

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
        print("Using 2013/2015 awards")
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315
    else:
        print("Using 2018/2019 awards")
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
