import os
import tweepy
import pandas as pd
from datetime import datetime, timezone

# Get Bearer Token from environment
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise Exception("❌ No BEARER_TOKEN found. Please set it as a GitHub Secret.")

# Initialize Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# Query parameters
QUERY = "Biharelection OR Biharvoting OR Biharpolling OR bihardemocratic2025 lang:en"
MAX_RESULTS = 20  # small batch to prevent long runs
DATA_DIR = "data"  # folder to save CSVs

# Create folder if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def collect_tweets():
    tweets = []
    try:
        response = client.search_recent_tweets(
            query=QUERY,
            max_results=MAX_RESULTS,
            tweet_fields=["created_at", "public_metrics", "lang"],
            expansions=["author_id"],
            user_fields=["username", "name"]
        )

        if response.data:
            users = {u.id: u for u in response.includes["users"]}
            for tweet in response.data:
                user = users.get(tweet.author_id)
                tweets.append({
                    "time": tweet.created_at,
                    "id": tweet.id,
                    "text": tweet.text,
                    "username": user.username if user else "",
                    "name": user.name if user else "",
                    "retweets": tweet.public_metrics["retweet_count"],
                    "likes": tweet.public_metrics["like_count"]
                })

    except tweepy.errors.TooManyRequests:
        print("⚠️ Rate limit reached. Skipping this run.")
    except tweepy.errors.Unauthorized:
        print("❌ Unauthorized! Check your BEARER_TOKEN.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

    return tweets

if __name__ == "__main__":
    data = collect_tweets()
    if not data:
        print("⚠️ No tweets collected this run.")
    else:
        df = pd.DataFrame(data)
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        filename = os.path.join(DATA_DIR, f"tweets_{now}.csv")
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} tweets to {filename}")
