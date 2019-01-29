import json
import sys
import nltk
import time
import random
import csv

def main():
    timer = time.time()

    # load in the tweets
    tweet_file = sys.argv[1]

    # optional hardcoding award categories
    if(len(sys.argv) > 2):
        awards = sys.argv[2]
        awards = awards.split(',')
    
    # optional hardcoding nominees
    if(len(sys.argv) > 3):
        nominees = sys.argv[3]
        nominees = nominees.split(',')
    

    # transform tweets into a useful form

    # read from file
    with open(tweet_file) as f:
        tweets = json.load(f)

    # reduce to a controllable number of tweets
    if(len(tweets)) > 5000:
        tweets = random.sample(tweets, 5000)

    # take only text
    tweet_text = []
    for i in tweets:
        tweet_text.append(i['text'])

    # check if it works
    print(FindWinner(tweet_text, "Foreign Film", ["Force Majeure", "Gett", "Ida", "Tangerines", "Leviathan"]))

    # check the timing
    print(time.time() - timer)

def FindWinner(tweets, award, nominees):
    # reduce to tweets about the desired award and nominee
    relevant_tweets = [tweet for tweet in tweets if award in tweet]

    # find the nominee mentioned most often
    max_nominee = nominees[0]
    max_count = 0

    for nominee in nominees:
        count = 0
        for tweet in relevant_tweets:
            if(nominee in tweet):
                count += 1
        
        if count > max_count:
            max_count = count
            max_nominee = nominee

    return max_nominee


if __name__ == '__main__':
    main()