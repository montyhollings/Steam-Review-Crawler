import requests
import json
import math
import urllib.parse
import copy


class ReviewCrawler:
    def __init__(self, gamename, franchise, appid=1382330):
        # Hard code source as per spec,
        # Not sure if you should be able to change appId by input etc
        self.gameName = gamename
        self.franchise = franchise
        self.total_review_count = 0
        self.total_review_batches = 0
        self.review_counter = 0
        self.formatted_reviews = {}
        self.parameters = {}
        self.batch_reviews = {}
        self.number_in_batch = 0
        self.cursor = "*"
        self.source = "steam"
        self.appId = appid

    def setup_parameters(self, language, date, per_page):
        # Setup parameters for the requests
        self.parameters = {
            "filter": "all",
            "language": language,
            "day_range": date,
            "num_per_page": per_page,
            "cursor": self.cursor
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
        self.total_review_count = response.json()['query_summary']['total_reviews']
        self.total_review_batches = math.ceil(self.total_review_count / self.parameters['num_per_page'])
        self.review_batch_loop()

    def review_batch_loop(self):
        # Loop over the amount of review batches
        for index in range(self.total_review_batches):
            # Send request
            request_response = self.send_request()
            # Format request and save properties
            json_response = request_response.json()
            self.parameters['cursor'] = json_response['cursor']
            self.number_in_batch = json_response['query_summary']['num_reviews']
            self.batch_reviews = json_response['reviews']
            # For each batch of reviews, we need to process and format them
            self.process_reviews()

    def send_request(self):
        response = requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1&num_per_page=100', params=self.parameters)
        return response

    def process_reviews(self):
        # Loop over every review (always 100 per batch)
        # send json to be formatted along with its index which I shall use as the ID for now
        for counter in range(self.number_in_batch):
            self.formatted_reviews[self.review_counter] = self.format_review(self.batch_reviews[counter],
                                                                             self.review_counter)
            self.review_counter += 1

    def format_review(self, review_instance, review_id):
        # Return review in desired format
        # TODO: finish author hash instead of current hack
        # TODO: finish proper UUID for each review
        return {
            'id': review_id,
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
NewCrawler.display_reviews()
