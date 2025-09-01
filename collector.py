import os
import csv
from datetime import datetime
import pandas as pd

# Try Tweepy (Twitter API v2)
try:
    import tweepy
except ImportError:
    tweepy = None

# Try snscrape
try:
    import snscrape.modules.twitter as sntwitter
except ImportError:
    sntwitter = None


def collect_with_tweepy(bearer_token, query, max_results=50):
    """Collect tweets using Twitter API v2 with Tweepy."""
    client = tweepy.Client(bearer_token=bearer_token)

    tweets = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=["created_at", "author_id", "text"]
    )

    data = []
    if tweets.data:
        for tweet in tweets.data:
            data.append([tweet.created_at, tweet.author_id, tweet.text])
    return data


def collect_with_snscrape(query, max_results=50):
    """Collect tweets using snscrape (no API key required)."""
    data = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= max_results:
            break
        data.append([tweet.date, tweet.user.username, tweet.content])
    return data


if __name__ == "__main__":
    # Search query (edit keywords as you like)
    query = "Biharelection OR Biharvoting OR Biharpolling OR bihardemocratic2025 lang:en"

    # Output file with timestamp
    filename = f"tweets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    # Check if Bearer Token is available
    bearer_token = os.getenv("BEARER_TOKEN")

    if bearer_token and tweepy is not None:
        print("✅ Using Twitter API with Tweepy...")
        data = collect_with_tweepy(bearer_token, query, max_results=50)
    elif sntwitter is not None:
        print("⚡ Falling back to snscrape...")
        data = collect_with_snscrape(query, max_results=50)
    else:
        raise Exception("❌ No method available: install tweepy or snscrape!")

    # Save to CSV
    df = pd.DataFrame(data, columns=["created_at", "author", "text"])
    df.to_csv(filename, index=False, encoding="utf-8")

    print(f"💾 Saved {len(df)} tweets to {filename}")
