# knews_py/src/config.py

# Default RSS feed URLs
DEFAULT_FEED_URLS = [
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "https://feeds.foxnews.com/foxnews/latest",
    "https://www.npr.org/rss/rss.php?id=1001",
    # Add more default feeds here
]

# Configuration for newspaper3k, if used (example)
# from newspaper import Config
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
# NP_CONFIG = Config()
# NP_CONFIG.browser_user_agent = USER_AGENT
# NP_CONFIG.request_timeout = 10

# API Keys (if any, keep them secure and ideally load from environment variables)
# EXAMPLE_API_KEY = "YOUR_API_KEY_HERE"

# Other configurations
MAX_ARTICLES_PER_FEED = 50
OUTPUT_DIRECTORY = "output_data" # Example, adjust as needed

# Domains to exclude articles from
EXCLUDED_DOMAINS = [
    "khan.co.kr",
    "rss.kmib.co.kr",
    "ddanzi.com",
    "mediatoday.co.kr",
    # Add more domains here as needed
]
