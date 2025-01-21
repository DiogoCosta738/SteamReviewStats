import requests
from bs4 import BeautifulSoup
import datetime
import json

import plots

months = {
    "January" : 1,
    "February": 2,
    "March" : 3,
    "April" : 4,
    "May" : 5,
    "June" : 6,
    "July" : 7,
    "August" : 8,
    "September" : 9,
    "October" : 10,
    "November" : 11,
    "December" : 12
}
# votes: review_box > header (class of div)
# recommendation: review_box > review_box_content > rightcol > vote_header > thumb > img src "[...]thumbUp.png"
# review text: review_box > review_box_content > content
# date: review_box > review_box_content > posted (class of div)

def parse_date(date_text):
    tokens = date_text.split('.')
    tokens = tokens[0].split(' ')
    day = 0
    try:
        day = int(tokens[1])
    except:
        day = 1
        assert False, "Failed to parse day as int"
    month = months[tokens[2].replace(',', '')]
    year = 2025
    if len(tokens) >= 4:
        try:
            year = int(tokens[3])
        except:
            year = 2025
            assert False, "Failed to parse year"
    return datetime.date(year = year, month = month, day = day)

def parse_thumb(thumb_text):
    if thumb_text.find("thumbsUp") != -1:
        return True
    elif thumb_text.find("thumbsDown"):
        return False
    else:
        return "unknown"

def parse_votes(votes_text):
    votes_text = votes_text.replace('\n', '')
    tokens = list(filter(None, votes_text.split('\t')))
    helpful = tokens[0].split(' ')[0]
    if helpful == "No":
        helpful = 0
    else:
        try:
            helpful = int(helpful)
        except:
            helpful = 0
            assert False, "Failed to parse helpful"

    funny = 0
    if len(tokens) == 2:
        try:
            funny = int(tokens[1].split[' '][0])
        except:
            funny = 0
            # assert False, "Failed to parse helpful"

    return helpful, funny

def parse_content(content_text):
    return content_text.replace('\t', '')


def get_game_name_from_store(app_id):
    url = f"https://store.steampowered.com/app/{app_id}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('div', {'class': 'apphub_AppName'})
        return title_tag.text if title_tag else "Game not found"
    else:
        return "Error: Unable to fetch page"

def gather_review_data():
    # Fetch the webpage
    url = "https://steamcommunity.com/id/diogocosta738/recommended/?p="

    index = 1
    review_elems = []
    while True:
        print("Starting to parse page", index, "...")
        response = requests.get(url + str(index))

        soup = BeautifulSoup(response.text, 'html.parser')
        review_boxes = soup.find_all(class_="review_box")
        for rb in review_boxes:
            review_elems.append(rb)

        if len(review_boxes) == 0:
            break

        index += 1

    reviews_data = []
    for review_box in review_elems:
        votes = review_box.find('div', class_='header') \
            .text

        thumb = review_box.find('div', class_='review_box_content') \
            .find('div', class_='rightcol') \
            .find('div', class_='vote_header') \
            .find('div', class_='thumb') \
            .find('img').get('src')

        text = review_box.find('div', class_='review_box_content') \
            .find('div', class_='content') \
            .text

        date = review_box.find('div', class_='review_box_content') \
            .find('div', class_='posted') \
            .text

        store_page = review_box.find('div', class_='review_box_content') \
            .find('div', class_='leftcol') \
            .find('a') \
            .get('href')

        votes = parse_votes(votes)
        helpful = votes[0]
        funny = votes[1]

        tokens = store_page.split("/")
        app_id = tokens[len(tokens) - 1]
        #game_name = get_game_name_from_store(app_id)

        review_dict = dict()
        review_dict["date"] = parse_date(date)
        review_dict["positive"] = parse_thumb(thumb)
        review_dict["helpful"] = helpful
        review_dict["funny"] = funny
        review_dict["text"] = parse_content(text)
        review_dict["store-page"] = store_page
        #review_dict["game"] = game_name
        reviews_data.append(review_dict)

    return reviews_data

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            # Serialize datetime/date objects as ISO format strings
            return obj.isoformat()
        return super().default(obj)

# Custom Decoder
def date_hook(dct):
    for key, value in dct.items():
        # Check if a string matches ISO datetime format
        try:
            dct[key] = datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError):
            pass
    return dct

def print_review(review_dict):
    word_count = len(review_dict["text"].split(' '))
    helpful_count = review_dict["helpful"]
    store_page = review_dict["store-page"]
    date = review_dict["date"]
    verdict = "positive" if review_dict["positive"] else "negative"
    print("+{0} - {1} - Word count: {2}".format(helpful_count, verdict, word_count))
    print("Storepage: {0}".format(store_page))
    print("Written in {0}".format(date))
    print("----")

def write_review_data():
    reviews_data = gather_review_data()
    json_string = json.dumps(reviews_data, indent=4, cls=DateTimeEncoder)

    f = open("reviews_data.json", "w")
    f.write(json_string)
    f.close()

def read_review_data():
    f = open("reviews_data.json", "r")
    json_string = f.read()
    f.close()
    json_dict = json.loads(json_string, object_hook=date_hook)
    return json_dict

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #write_review_data()

    reviews = read_review_data()
    reviews.sort( key = lambda review_dict: review_dict["helpful"])

    positive_count = 0
    for review in reviews:
        if review["positive"]:
            positive_count += 1
        print_review(review)
    print("Positive reviews: {0}/{1}".format(positive_count, len(reviews)))

    plots.plot_wordcount_by_month(reviews)
    plots.plot_helpful_by_month(reviews)
    plots.plot_by_helpful(reviews)
    plots.plot_by_wordcount(reviews)
    print("Job's done!")
