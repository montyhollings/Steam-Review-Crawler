import requests
import json
import math
import urllib.parse
import copy
import os
from slugify import slugify
import datetime
import time


def setup_date_filter():
    date_valid = False
    while date_valid == False:
        filter_from = input('Please enter the date you wish to filter from in format [yyyy-mm-dd]: ')
        try:
            from_date = datetime.datetime.strptime(filter_from, '%Y-%m-%d')
            date_valid = True
        except ValueError:
            print('Incorrect please try again, e.g 2001-01-01')
    todays_date = datetime.datetime.now()
    return (todays_date - from_date).days


def initialise_crawler(game_name="Persona 5", franchise="Persona 5", filter_range=30000):
    print('Starting Crawler...')
    NewCrawler = ReviewCrawler(game_name, franchise, filter_range)
    print('Setting up crawler configuration...')
    NewCrawler.setup_parameters()
    print('Crawling...')
    # NewCrawler.get_reviews()


class ReviewCrawler:
    def __init__(self, gamename, franchise, filter_range, appid=1382330):
        # Hard code source as per spec,
        # Not sure if you should be able to change appId by input etc
        self.gameName = gamename
        self.franchise = franchise
        self.filter_range = filter_range
        self.total_review_count = 0
        self.request_loop_count = 0
        self.file_count = 0
        self.review_counter = 0
        self.formatted_reviews = {}
        self.parameters = {}
        self.reviews = {}
        self.number_in_batch = 0
        self.cursor = "*"
        self.source = "steam"
        self.appId = appid


    def setup_parameters(self, language="english", per_page="100", review_type="all", purchase_type="all"):
        # Setup parameters for the requests
        self.parameters = {
            "filter": "all",
            "language": language,
            "day_range": self.filter_range,
            "cursor": self.cursor,
            "review_type": review_type,
            "purchase_type": purchase_type,
            "num_per_page": per_page,
        }
        # Get the total review count so we know the loop indexes
        self.get_total_review_count()

    def get_total_review_count(self):
        # TODO: accept date parameters
        # Overwrite the num per page to 1, this will save speed by making the response much smaller
        temp_parameters = copy.copy(self.parameters)
        print(self.parameters)
        temp_parameters['num_per_page'] = "1"
        response = requests.Request("GET",
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1', data=temp_parameters)
        prepared = response.prepare()
        pretty_print_POST(prepared)
        # Grab the total number of reviews in the response
        # Divide that number by the amount per page and round up the result to get the number of batches needed
        # self.total_review_count = int(response.json()['query_summary']['total_reviews'])
        # self.request_loop_count = math.floor(self.total_review_count / 100)
        # self.file_count = math.ceil(self.total_review_count / 200)
        # print('total reviews: ' + str(self.total_review_count))

    def get_reviews(self):

        for i in range(self.request_loop_count):
            print('------ LOOP ------ ')
            print('index: ' + str(self.review_counter))
            print('old_cursor: ' + str(self.parameters['cursor']))
            print('pre-add reviews=: ' + str(self.reviews.keys()))
            if i == 0:
                slug = "*"
            else:
                slug = slugify(self.parameters['cursor'])

            if slug in self.reviews:
                print('cursor: ' + str(self.parameters['cursor'] + ' is a dupe'))
                self.parameters['cursor'] = str(urllib.parse.quote(self.reviews[slug]['cursor']))
                continue

            response = self.send_request()

            json_response = response.json()
            print('raw_cursor: ' + str(json_response['cursor']))
            self.parameters['cursor'] = str(urllib.parse.quote(json_response['cursor']))
            print('encoded_cursor: ' + str(self.parameters['cursor']))
            print('slug: ' + str(slug))
            self.reviews[slug] = json_response
            print('adding: ' + str(slug) + ' to self.reviews')
            self.review_counter += 1
            self.request_loop_count -= 1
            print(self.request_loop_count)
            time.sleep(1.5)

        # LOOP ENDS ALL REVIEWS ADDED TO SELF.REVIEWS
        for key, value in self.reviews.items():
            for x in value['reviews']:
                self.formatted_reviews[self.review_counter] = self.format_review(x)
                self.review_counter += 1

        self.display_reviews()
        print(' LOOPS: ' + str(self.request_loop_count))
        print(str(len(self.reviews)))

    def send_request(self):
        return requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1&', params=self.parameters)

    def format_review(self, review_instance):
        # Return review in desired format
        # TODO: finish proper UUID for each review
        return {
            'id': self.review_counter,
            'author': hash(review_instance['author']['steamid']),
            'date': review_instance['timestamp_created'],
            'hours': review_instance['author']['playtime_at_review'],
            'content': review_instance['review'],
            'comments': review_instance['comment_count'],
            'source': self.source,
            'helpful': review_instance['votes_up'],
            'funny': review_instance['votes_funny'],
            'recommended': review_instance['voted_up'],
            'franchise': self.franchise,
            'gameName': self.gameName,
        }

    def display_reviews(self):
        # Print out each review to file
        with open('data.json', 'w') as outfile:
            json.dump(self.formatted_reviews, outfile, indent=4)


# Hard core game name & franchise for now to something temporary
game_name = input('Please enter the name of the game you are crawling: ')
franchise = input('Please enter the name of the game you are crawling: ')
filter_by_date = input('If you wish to enter by date, please enter Y or y, else hit enter: ')

if(filter_by_date == "Y" or filter_by_date == "y"):
    date_range = setup_date_filter()
else:
    date_range = None

initialise_crawler(game_name, franchise, date_range)
