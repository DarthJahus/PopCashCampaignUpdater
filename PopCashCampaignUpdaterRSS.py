# Jahus, 2023-07-24
# API documentation: http://docs.api.popcash.net/#/Advertiser%20%2F%20Campaigns/put_campaigns__id_

import feedparser
import requests
import time
import json

__last_processed_timestamp = None
__log_file = open("latest.log", 'a', encoding="utf-8")


def log_to_file(text):
    __log_file.write(text)


def pc_increase_campaign_budget(campaign_id, api_key, budget_delta):
    url = f"https://api.popcash.net/campaigns/{campaign_id}"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "adjustBudget": budget_delta
    }
    response = requests.put(url, headers=headers, json=data)
    return (response.status_code == 200)


def check_new_article_in_rss(feed_url):
    global __last_processed_timestamp
    feed = feedparser.parse(feed_url)
    if 'entries' in feed:
        latest_article = feed.entries[0]
        article_timestamp = latest_article.get('published_parsed')
        article_id = latest_article.get('id')
        if __last_processed_timestamp is None or article_timestamp > __last_processed_timestamp:
            __last_processed_timestamp = article_timestamp
            return True, article_id
        else:
            return False, article_id
    return False, None


if __name__ == "__main__":
    __config = dict()
    with open("config.json", 'r', encoding="utf-8") as _config_file:
        __config = json.loads(_config_file.read())
    
    while True:
        log_to_file("%s\n Getting updates via RSS..." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        new_article_available, article_id = check_new_article_in_rss(__config["rss_link"])
        if new_article_available:
            if pc_increase_campaign_budget(__config["campaign_id"], __config["api_key"], __config["budget_delta"]):
                log_to_file(f"Campaign {__config['campaign_id']} budget increased successfully by {__config['budget_delta']} $\n for new article {article_id}\n published on %s." % time.strftime("%Y-%m-%d %H:%M:%S", __last_processed_timestamp))
            else:
                log_to_file(f"Failed to increase budget for campaign {__config['campaign_id']}.")
        else:
            log_to_file(f"No new articles available in the RSS feed.\n Last article: {article_id}\n published on %s." % time.strftime("%Y-%m-%d %H:%M:%S", __last_processed_timestamp))
        log_to_file("Waiting %i minutes before checking for updates...\nPress CTRL+C to exit." % (__config["update_period"] * 60), end='\r')
        time.sleep(__config["update_period"] * 60)

__log_file.close()
