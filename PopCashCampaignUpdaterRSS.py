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
        

__last_processed_timestamp = {}
__log_file = open("latest.log", 'a', encoding="utf-8")
sys.stdout = DoubleOut(__log_file)


def pc_increase_campaign_budget(campaign_id, api_key, budget_delta, update_url=False):
    url = f"https://api.popcash.net/campaigns/{campaign_id}"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "adjustBudget": 0.1 + ((budget_delta - 0.1) * int(not __config["debug"]))
    }
    if update_url:
        data["url"] = update_url
    response = requests.put(url, headers=headers, json=data, timeout=10)
    return (response.status_code == 200)


def check_new_article_in_rss(website):
    feed = feedparser.parse(website["rss_link"])
    if "entries" in feed:
        if len(feed["entries"]) > 0:
            for _latest_article in feed.entries[0:3]:
                _article_timestamp = _latest_article.get('published_parsed')
                _article_id = _latest_article.get('id')
                _article_url = _latest_article.get('link')
                if (_latest_article.get('author') in website["authors"] or len(website["authors"]) == 0) and (website["rss_link"] not in __last_processed_timestamp or _article_timestamp > __last_processed_timestamp[website["rss_link"]]):
                    __last_processed_timestamp[website["rss_link"]] = _article_timestamp
                    return True, _article_id, _article_url
            return False, feed.entries[0].get('id'), feed.entries[0].get('link')
        return False, None, None
    return False, None, None


if __name__ == "__main__":
    __config = dict()
    with open("config.json", 'r', encoding="utf-8") as _config_file:
        __config = json.loads(_config_file.read())
    
    while True:
        for _website in __config["websites"]:
            if __config["websites"][_website]["rss_link"]:
                print("%s\n Getting updates via RSS for %s..." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), _website))
                new_article_available, article_id, article_url = check_new_article_in_rss(__config["websites"][_website])
                if not __config["websites"][_website]["update_url"]:
                    article_url = False
                if __config["websites"][_website]["append_utm"]:
                    if '?' in article_url:
                        article_url += "&" + __config["websites"][_website]["append_utm"]
                    else:
                        article_url += "?" + __config["websites"][_website]["append_utm"]
                if new_article_available:
                    if pc_increase_campaign_budget(__config["websites"][_website]["campaign_id"], __config["websites"][_website]["api_key"], __config["websites"][_website]["budget_delta"], update_url=article_url):
                        print(f"Campaign {__config['websites'][_website]['campaign_id']} budget increased successfully by {__config['websites'][_website]['budget_delta']} $\n for new article {article_id}\n published on %s." % time.strftime("%Y-%m-%d %H:%M:%S", __last_processed_timestamp[__config["websites"][_website]["rss_link"]]))
                    else:
                        print(f"Failed to increase budget for campaign {__config['websites'][_website]['campaign_id']}.")
                else:
                    print(f"No new articles available in the RSS feed.\n Last article: {article_id}.")
                print("Waiting %i seconds before checking for updates...\n" % (__config["update_period"] * (1 + 59 * int(not __config["debug"]))))
        time.sleep(__config["update_period"] * (1 + 59 * int(not __config["debug"])))

sys.stdout = sys.__stdout__
__log_file.close()
