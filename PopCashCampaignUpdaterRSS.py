# Jahus, 2023-07-24
# API documentation: http://docs.api.popcash.net/#/Advertiser%20%2F%20Campaigns/put_campaigns__id_

import feedparser
import requests
import time
import json
import sys


class DoubleOut:
    def __init__(self, file):
        self.file = file
    
    def write(self, text):
        self.file.write(text)
        sys.__stdout__.write(text)
    
    def flush(self):
        self.file.flush()
        

__last_processed_timestamp = None
__log_file = open("latest.log", 'a', encoding="utf-8")
sys.stdout = DoubleOut(__log_file)


def pc_increase_campaign_budget(campaign_id, api_key, budget_delta):
    url = f"https://api.popcash.net/campaigns/{campaign_id}"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "adjustBudget": 0.1 + ((budget_delta - 0.1) * int(not __config["debug"]))
    }
    response = requests.put(url, headers=headers, json=data)
    return (response.status_code == 200)


def check_new_article_in_rss(feed_url, authors):
    global __last_processed_timestamp
    feed = feedparser.parse(feed_url)
    if 'entries' in feed:
        for _latest_article in feed.entries[0:3]:
            _article_timestamp = _latest_article.get('published_parsed')
            _article_id = _latest_article.get('id')
            if (_latest_article.get('author') in authors) and (__last_processed_timestamp is None or _article_timestamp > __last_processed_timestamp):
                __last_processed_timestamp = _article_timestamp
                return True, _article_id
        return False, feed.entries[0].get('id')
    return False, None


if __name__ == "__main__":
    __config = dict()
    with open("config.json", 'r', encoding="utf-8") as _config_file:
        __config = json.loads(_config_file.read())
    
    while True:
        print("%s\n Getting updates via RSS..." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        new_article_available, article_id = check_new_article_in_rss(__config["rss_link"], __config["authors"])
        if new_article_available:
            if pc_increase_campaign_budget(__config["campaign_id"], __config["api_key"], __config["budget_delta"]):
                print(f"Campaign {__config['campaign_id']} budget increased successfully by {__config['budget_delta']} $\n for new article {article_id}\n published on %s." % time.strftime("%Y-%m-%d %H:%M:%S", __last_processed_timestamp))
            else:
                print(f"Failed to increase budget for campaign {__config['campaign_id']}.")
        else:
            print(f"No new articles available in the RSS feed.\n Last article: {article_id}.")
        print("Waiting %i seconds before checking for updates...\nPress CTRL+C to exit." % (__config["update_period"] * (1 + 59 * int(not __config["debug"]))), end='\r')
        time.sleep(__config["update_period"] * (1 + 59 * int(not __config["debug"])))

sys.stdout = sys.__stdout__
__log_file.close()
