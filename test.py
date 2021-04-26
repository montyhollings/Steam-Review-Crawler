import json
import math
import requests
import datetime


def initialise_crawler(game_name="Persona 5", franchise="Persona 5"):
    print('Starting Crawler...')
    NewCrawler = ReviewCrawler(game_name, franchise)
    print('Crawling...')
    NewCrawler.get_reviews()


class ReviewCrawler:
    def __init__(self, game_name, franchise_name, date=30000, app_id=1382330, language="english", per_page=100,
                 review_type="all",
                 purchase_type="all"):
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
        self.formatted_reviews = {}

    def get_reviews(self):
        response = self.get_review_batch()
        reviews = []

        print(response['query_summary'])
        reviews += response['reviews']
        self.total_reviews = reviews['query_summary']['total_reviews']
        total_batches = self.get_total_batches(response)

        cursor = response['cursor']

        for index in range(total_batches):
            batch_response = self.get_review_batch(cursor)
            reviews += batch_response['reviews']
            cursor = batch_response['cursor']

        print(response['query_summary']['total_reviews'])
        print(len(reviews))
        self.format_reviews(reviews)
        self.save_reviews()

    def get_total_batches(self, response):
        return math.ceil(response['query_summary']['total_reviews'] / self.per_page) - 1

    def get_review_batch(self, cursor='*'):

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
        file_id = 0
        review_id = 0
        files = math.ceil(self.total_reviews / 500)
        for i in range(files):
            for item in range(500):
                self.formatted_reviews[review_id] = {
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



    @staticmethod
    def save_reviews(self):
        with open('data.json', 'w') as outfile:
            json.dump(self.formatted_reviews, outfile, indent=4)


game_name = input('Please enter the name of the game you are crawling: ')
franchise = input('Please enter the franchise name of the game you are crawling: ')
initialise_crawler()
