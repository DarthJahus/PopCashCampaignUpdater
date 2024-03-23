## Config example

Create a `config.json` file and follow this template:

```json
{
	"websites": {
		"my.super-news.web": {
			"api_key": "such-sicret-key",
			"campaign_id": "123490",
			"rss_link": "https://awesome-doma.in/feed/",
			"budget_delta": 1,
			"authors": ["NotChatGPT", "Spectalist"],
            "update_url": false,
            "append_utm": "utm_source=popcash"
		},
		"not-copy-pasta.blog": {
			"api_key": "wow-other-key",
			"campaign_id": "119181",
			"rss_link": false,
			"budget_delta": 2,
			"authors": [],
            "update_url": true,
            "append_utm": false
		}
	},
	"update_period": 5,
    "debug": false
}

```

## Notes

- Use your domain name as website name in the config file.

- If `authors` is empty (`[]`), the script will not filter authors.

- If `update_url` is `true`, the script will push article URL to the campaign. However, be aware that PopCash will put the campaign on hold ("Pending") until they review and validate the URL.

- If you want to set UTM parameters, do so in `append_utm`. If not, set it to `false`.

- `PopCashClipboard.py` will read from clipboard and, if it finds a valid URL, will update the campaign corresponding to the URL's domain name.
