import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime

# Search query (you can change keywords here)
query = "Biharelection OR Biharvoting OR Biharpolling OR bihardemocractic2025 lang:en"

# Number of tweets to fetch per run
max_tweets = 100

# Collect tweets
tweets = []
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
    if i >= max_tweets:
        break
    tweets.append([tweet.date, tweet.user.username, tweet.content])

# Save tweets to CSV with timestamp
df = pd.DataFrame(tweets, columns=['Date', 'User', 'Content'])
filename = f"tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(filename, index=False)

print(f"Saved {len(df)} tweets to {filename}")
