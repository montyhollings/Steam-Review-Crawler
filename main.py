import requests
import json
import math
import urllib.parse
import copy
import os
from slugify import slugify
import time


class ReviewCrawler:
    def __init__(self, gamename, franchise, appid=1382330):
        # Hard code source as per spec,
        # Not sure if you should be able to change appId by input etc
        self.gameName = gamename
        self.franchise = franchise
        self.total_review_count = 0
        self.request_loop_count = 0
        self.review_counter = 0
        self.formatted_reviews = {}
        self.parameters = {}
        self.batch_reviews = {}
        self.reviews = {}
        self.number_in_batch = 0
        self.cursor = "*"
        self.source = "steam"
        self.appId = appid
        self.output_dir = os.getcwd()

    def setup_parameters(self, language="english", date="3650", per_page="100", review_type="all", purchase_type="all"):
        # Setup parameters for the requests
        self.parameters = {
            "filter": "all",
            "language": language,
            "day_range": date,
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
        temp_parameters['num_per_page'] = "1"
        response = requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1', params=temp_parameters)
        # Grab the total number of reviews in the response
        # Divide that number by the amount per page and round up the result to get the number of batches needed
        self.total_review_count = int(response.json()['query_summary']['total_reviews'])
        self.request_loop_count = math.floor(self.total_review_count / 100)
        print('total reviews: ' + str(self.total_review_count))

    def get_reviews(self):

        counter = 0
        for i in range(self.request_loop_count):
            print('------ LOOP ------ ')
            print('index: ' + str(counter))
            print('old_cursor: ' + str(self.parameters['cursor']))
            if i == 0:
                slug = "*"
            else:
                counter += 1
                slug = slugify(self.parameters['cursor'])

            if slug in self.reviews:
                self.parameters['cursor'] = urllib.parse.quote_plus(self.reviews[slug]['cursor'])
                continue

            response = self.send_request()

            json_response = response.json()
            print('raw_cursor: ' + str(json_response['cursor']))
            response_slug = slugify(json_response['cursor'])
            self.parameters['cursor'] = urllib.parse.quote_plus(json_response['cursor'])
            print('encoded_cursor: ' + str(self.parameters['cursor']))
            self.reviews[response_slug] = json_response
            print('------------')

            # LOOP ENDS ALL REVIEWS ADDED TO SELF.REVIEWS
        for key, value in self.reviews.items():
            for x in value['reviews']:
                self.formatted_reviews[self.review_counter] = self.format_review(x)
                self.review_counter += 1

        self.display_reviews()

    def send_request(self):
        return requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1&', params=self.parameters)

    def format_review(self, review_instance):
        # Return review in desired format
        # TODO: finish author hash instead of current hack
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
game_name = "Persona 5"
franchise = "Persona 5"

# Create a new ReviewCrawler Instance, passing our two hardcoded variables
NewCrawler = ReviewCrawler(game_name, franchise)
# Steam reviews came out in 2013. Ill be safe and round up so that's 3650 days
# Setting up temp variables outside of the class
day_range = 3650
language = "english"
num_per_page = 100
# Create new crawler instance
# Display reviews
NewCrawler.setup_parameters(language, day_range, num_per_page)
NewCrawler.get_reviews()
