import json
import math
import requests
import itertools


# Review chunking function

def chunks(data, SIZE=5000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in itertools.islice(it, SIZE)}


# Startup function which creates the new Crawler object
# Then actives the crawler
def initialise_crawler(game_name="Persona 5", franchise="Persona 5"):
    print('Starting Crawler...')
    NewCrawler = ReviewCrawler(game_name, franchise)
    print('Crawling...')
    NewCrawler.get_reviews()


class ReviewCrawler:
    def __init__(self, game_name, franchise_name, date=30000, app_id=1382330, language="english", per_page=100,
                 review_type="all",
                 purchase_type="all", reviews_per_file=5000):
        self.language = language
        self.date = date
        self.source = 'steam'
        self.app_id = app_id
        self.per_page = per_page
        self.review_type = review_type
        self.game_name = game_name
        self.total_reviews = 0
        self.franchise_name = franchise_name
        self.purchase_type = purchase_type
        self.current_review_id = 0
        self.reviews_per_file = reviews_per_file

    def get_reviews(self):
        reviews = []
        # Send the first request, load the reviews to memory
        response = self.get_review_batch()
        reviews += response['reviews']
        # Get total reviews and calculate total batches to loop over
        self.total_reviews = response['query_summary']['total_reviews']
        total_batches = self.get_total_batches(response)
        # Set second cursor from the response
        cursor = response['cursor']

        # Loop over total batch count, each time setting the cursor to the the one sent by the response
        # Save reviews to memory
        for index in range(total_batches):
            batch_response = self.get_review_batch(cursor)
            reviews += batch_response['reviews']
            cursor = batch_response['cursor']

        print('Total expected reviews: ' + str(response['query_summary']['total_reviews']))
        print('Resultant reviews: ' + str(len(reviews)))

        # Format, then save the reviews to storage
        formatted_reviews = self.format_reviews(reviews)
        self.save_reviews(formatted_reviews, self.reviews_per_file)

    def get_total_batches(self, response):
        # Subtracting one from the rounded division as arrays start at 0
        return math.ceil(response['query_summary']['total_reviews'] / self.per_page) - 1

    def get_review_batch(self, cursor='*'):
        # Set cursor to * on the first call to signal the start of the dataset
        response = requests.get(
            f'https://store.steampowered.com/appreviews/{self.app_id}?json=1', params={
                "filter": "recent",
                "language": self.language,
                "day_range": self.date,
                "cursor": cursor,
                "review_type": self.review_type,
                "purchase_type": self.purchase_type,
                "num_per_page": self.per_page,
            })

        return response.json()

    def format_reviews(self, reviews):
        # Loop over every review, providing them a unique ID
        # Set formatted reviews dict key to be the unique id
        # Hash author due to privacy
        review_id = 1
        formatted_reviews = {}
        for item in reviews:
            formatted_reviews[review_id] = {
                'id': self.current_review_id,
                'author': hash(item['author']['steamid']),
                'date': item['timestamp_created'],
                'hours': item['author']['playtime_at_review'],
                'content': item['review'],
                'comments': item['comment_count'],
                'source': self.source,
                'helpful': item['votes_up'],
                'funny': item['votes_funny'],
                'recommended': item['voted_up'],
                'franchise': self.franchise_name,
                'gameName': self.game_name,
            }
            review_id += 1
        return formatted_reviews

    @staticmethod
    def save_reviews(reviews, reviews_per_file):
        # As we want a maximum of 5k reviews per file we need to
        # split the dictionary of reviews into groups of up to 5k
        list_of_dicts = [item for item in chunks(reviews, reviews_per_file)]

        # Save the file name simply with a number prefix to represent order
        # Loop over each group of 5k reviews, saving them to a file
        file_counter = 1
        for batch in list_of_dicts:
            with open(f'reviews-{file_counter}.json', 'w') as outfile:
                json.dump(batch, outfile, indent=4)
                file_counter += 1


# Script start
# Take gamename and franchise inputs, provide them to the initialisation function
# Start crawler
game_name = input('Please enter the name of the game you are crawling: ')
franchise = input('Please enter the franchise name of the game you are crawling: ')
initialise_crawler(game_name, franchise)
