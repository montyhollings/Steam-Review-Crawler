import requests
import json
import math
import urllib.parse
import copy
import os
from slugify import slugify
print(os.getcwd())
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
        self.output_dir = os.getcwd()

    def setup_parameters(self, language="english", date="3650", per_page="100", review_type="all", purchase_type="all"):
        # Setup parameters for the requests
        self.parameters = {
            "filter": "all",
            "language": language,
            "day_range": date,
            "num_per_page": per_page,
            "cursor": self.cursor,
            "review_type": review_type,
            "purchase_type": purchase_type,
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

    def get_reviews(self):
        print(self.total_review_count)
        for i in range(math.floor(self.total_review_count / 100)):
            print(i)
            output_file_path = self.get_filepath()
            if os.path.exists(output_file_path):
                self.cursor = self.get_cursor_from_file()
                continue
            else:
                print('ERROR')
            response = self.send_request()
            if response.status_code == 200:
                json_response = response.json()
                self.cursor = urllib.parse.quote(json_response['cursor'])
                with open(output_file_path, "w") as f:
                    json.dump(fp=f, obj=json_response, indent=4)
            else:
                print('ERROR')
                # self.dump_to_file(json_response, output_file_path)
        # Loop over the amount of review batches
        while self.total_review_count > 0:

            # Send request
            request_response = self.send_request()
            # Format request and save properties
            json_response = request_response.json()
            self.parameters['cursor'] = json_response['cursor']
            self.number_in_batch = json_response['query_summary']['num_reviews']
            self.batch_reviews = json_response['reviews']
            # For each batch of reviews, we need to process and format them

    def send_request(self):
        return requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1&', params=self.parameters)

    def format_review(self, review_instance, review_id):
        # Return review in desired format
        # TODO: finish author hash instead of current hack
        # TODO: finish proper UUID for each review
        return {
            'id': review_id,
            'review_counter': self.total_review_count,
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

    def dump_to_file(self, json_request, file_path):
        with open(file_path, "w") as path:
            json.dump(path, json_request)

    def get_filepath(self):
        return os.path.join(
            self.output_dir,
            f"BATCH-{slugify(self.cursor)}.json"
        )

    def get_cursor_from_file(self):

        find_cursor_in = self.get_filepath()
        with open(find_cursor_in, "r") as f:
            v = json.load(f)
            cursor = urllib.parse.quote(v['cursor'])
            return cursor


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
