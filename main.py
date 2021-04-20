import requests
import json

app_id = 1382330
reviews_response = requests.get(f'https://store.steampowered.com/appreviews/{app_id}?json=1')
print(reviews_response.json())
