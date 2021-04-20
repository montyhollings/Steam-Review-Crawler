import requests
import json
import math

class ReviewCrawler:
    def __init__(self, gamename, franchise):
        # Hard code source as per spec,
        # Not sure if you should be able to change appId by input etc
        self.gameName = gamename
        self.franchise = franchise
        self.total_review_count = 0
        self.total_review_batches = 0
        self.formatted_reviews = {}
        self.batch_reviews = {}
        self.source = "steam"
        self.appId = 1382330

    def get_total_review_count(self, request_parameters = False):
        # TODO: accept date parameters
        response = requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1&num_per_page=1')
        self.total_review_count = response.json()['query_summary']['total_reviews']
        self.total_review_batches = math.ceil(self.total_review_count / 100)

    def initiate_crawler(self):
        # Get total amount of reviews so we know how many to loop over:
        self.get_total_review_count()

        # Send request, using our appID to pull back 100 reviews
        reviews_response = requests.get(
            f'https://store.steampowered.com/appreviews/{self.appId}?json=1&num_per_page=100')

        # Save the json response and save the reviews to a property on the class
        json_response = reviews_response.json()
        self.batch_reviews = json_response['reviews']

    def process_reviews(self):
        # Loop over every review (always 100 per batch)
        # send json to be formatted along with its index which I shall use as the ID for now
        for counter in range(100):
            self.formatted_reviews[counter] = self.format_review(self.batch_reviews[counter], counter)

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
        # Print out each review to console
        for y in self.formatted_reviews:
            print(self.formatted_reviews[y])

# Hard core game name & franchise for now to something temporary
game_name = "Persona 5"
franchise = "Persona 5"

# Create a new ReviewCrawler Instance, passing our two hardcoded variables
NewCrawler = ReviewCrawler(game_name, franchise)
# Request the reviews, process & format, then display to the users console
NewCrawler.initiate_crawler()
NewCrawler.process_reviews()
NewCrawler.display_reviews()
