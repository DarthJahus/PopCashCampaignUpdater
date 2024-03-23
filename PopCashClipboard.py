# Jahus, 2024-03-23
# API documentation: http://docs.api.popcash.net/#/Advertiser%20%2F%20Campaigns/put_campaigns__id_

import json
from winsound import Beep
import requests
from urllib.parse import urlparse
import pyperclip as clipboard


__config = dict()


def check_url(url):
    try:
        _parse = urlparse(url)
        return _parse.hostname
    except Exception as e:
        print(e)
        return False


def pc_edit_campaign(campaign_id, api_key, budget_delta, new_url=False):
    url = f"https://api.popcash.net/campaigns/{campaign_id}"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "adjustBudget": 0.1 + ((budget_delta - 0.1) * int(not __config["debug"]))
    }
    if new_url:
        data["url"] = new_url
    response = requests.put(url, headers=headers, json=data, timeout=10)
    print(response.text)
    return response.status_code == 200


if __name__ == "__main__":
    with open("config.json", 'r', encoding="utf-8") as _config_file:
        __config = json.loads(_config_file.read())
    _url = clipboard.paste()
    _host = check_url(_url)
    if _host:
        if _host in __config["websites"]:
            if pc_edit_campaign(
                __config["websites"][_host]["campaign_id"],
                __config["websites"][_host]["api_key"],
                __config["websites"][_host]["budget_delta"],
                _url
            ):
                Beep(400, 1000)
                exit(0)
    print('Error updating campaign.')
    Beep(800, 1000)
    exit(1)
