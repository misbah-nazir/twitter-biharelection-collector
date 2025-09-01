import os
import requests
import pandas as pd
from datetime import datetime

# Load token from environment
bearer_token = os.getenv("BEARER_TOKEN")
headers = {"Authorization": f"Bearer {bearer_token}"}

# Twitter search query
query = "election OR voting OR democracy lang:en -is:retweet"

url = "https://api.twitter.com/2/tweets/search/recent"
params = {
    "query": query,
    "max_results": 10,   # keep small for testing
    "tweet.fields": "created_at,text,author_id"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    raise Exception(f"Error fetching tweets: {response.text}")

tweets = response.json().get("data", [])

# Save to CSV
df = pd.DataFrame(tweets)
df["fetched_at"] = datetime.utcnow()

csv_file = "tweets.csv"
if os.path.exists(csv_file):
    df_old = pd.read_csv(csv_file)
    df = pd.concat([df_old, df], ignore_index=True)

df.to_csv(csv_file, index=False)
print(f"Saved {len(tweets)} tweets to {csv_file}")
