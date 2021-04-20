import requests
import json

class ReviewCrawler:
    def __init__(self, gamename, franchise):
        self.gameName = gamename
        self.franchise = franchise
        self.reviews = {}
        self.source = "steam"
        self.appId = 1382330

    def get_reviews(self):
        reviews_response = requests.get(f'https://store.steampowered.com/appreviews/{self.appId}?json=1&num_per_page=100')
        json_response = reviews_response.json()
        self.reviews = json_response['reviews']
        self.display_reviews()

    def display_reviews(self):
        for y in range(100):
            print(self.reviews[y])



game_name = "Persona 5"
franchise = "Persona 5"
NewCrawler = ReviewCrawler(game_name, franchise)
NewCrawler.get_reviews()
