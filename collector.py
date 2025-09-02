import os
import tweepy
import pandas as pd
from datetime import datetime, timezone

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise Exception("❌ No BEARER_TOKEN found. Please set it as a GitHub Secret.")

client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

QUERY = "Biharelection OR Biharvoting OR Biharpolling lang:en"
MAX_RESULTS = 20
DATA_DIR = "data"
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
    tweet_count = len(data)
    print(f"📊 Collected {tweet_count} tweets this run.")

    if tweet_count > 0:
        df = pd.DataFrame(data)
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        filename = os.path.join(DATA_DIR, f"tweets_{now}.csv")
        df.to_csv(filename, index=False)
        print(f"✅ Saved {tweet_count} tweets to {filename}")
    else:
        print("⚠️ No tweets collected this run.")
