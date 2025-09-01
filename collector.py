import os
import tweepy
import pandas as pd
from datetime import datetime, timezone

# --- Twitter API setup ---
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not BEARER_TOKEN:
    raise Exception("❌ No BEARER_TOKEN found. Please set it as a GitHub Secret.")

client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# --- Search settings ---
QUERY = "Biharelection OR Biharvoting OR Biharpolling OR bihardemocratic2025 lang:en"
MAX_RESULTS = 50  # number of tweets per run

# --- Collect tweets ---
def collect_tweets():
    tweets = []
    response = client.search_recent_tweets(
        query=QUERY,
        max_results=MAX_RESULTS,
        tweet_fields=["created_at", "public_metrics", "lang"],
        user_fields=["username", "name"],
        expansions=["author_id"]
    )

    if response.data:
        users = {u["id"]: u for u in response.includes["users"]}
        for tweet in response.data:
            user = users.get(tweet.author_id, {})
            tweets.append({
                "time": tweet.created_at,
                "id": tweet.id,
                "text": tweet.text,
                "username": user.get("username"),
                "name": user.get("name"),
                "retweets": tweet.public_metrics["retweet_count"],
                "likes": tweet.public_metrics["like_count"]
            })
    return tweets

# --- Save to CSV ---
if __name__ == "__main__":
    data = collect_tweets()
    if not data:
        print("⚠️ No tweets collected this run.")
    else:
        df = pd.DataFrame(data)
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        filename = f"tweets_{now}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} tweets to {filename}")
