## Requirements:
- Python3+
- [Requests](https://pypi.org/project/requests/)

## Use

Main.py contains the entire script as sadly I havent had time to separate the class and functions. 

If you wish to change the game to crawl reviews on or the total number of reviews per file, change the value of app_id or reviews_per_file in the crawler constuctor respectively.
Instructions:
1. Run main.py
2. Input game name (hit enter for default)
3. Input franchise name (hit enter for default)
4. View reviews in reviews-x.json where x is the file number.

## Example

There is a copy of the script run on app id 1382330 (Persona 5) in the repo under reviews-1.json.
To regenerate these exact results, simply run the script and enter Persona 5 as the game name and franchise
