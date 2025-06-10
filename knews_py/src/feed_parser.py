# knews_py/src/feed_parser.py

import feedparser
import requests
from typing import List, Dict, Optional
from .models import FeedSpec # Import FeedSpec
import os # For __main__ block path check

# This definition might be needed if we run __main__ and want to use dummy data from default paths
BASE_DIR_FP = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PUBLISHERS_PATH_FP = os.path.join(BASE_DIR_FP, '..', 'data', 'publishers.csv')


def fetch_feed(feed_url: str, timeout: int = 10) -> Optional[feedparser.FeedParserDict]:
    """
    Fetches an RSS feed from the given URL.
    """
    try:
        response = requests.get(feed_url, timeout=timeout)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if feed.bozo:
            print(f"Warning: Feed from {feed_url} may be ill-formed. Bozo exception: {feed.bozo_exception}")
        return feed
    except requests.exceptions.RequestException as e:
        print(f"Error fetching feed from {feed_url}: {e}")
        return None
    except Exception as e: # Catch any other unexpected errors during parsing
        print(f"An unexpected error occurred while processing {feed_url}: {e}")
        return None

def parse_feed_entries(feed: feedparser.FeedParserDict, feed_spec: FeedSpec) -> List[Dict]: # Added feed_spec argument
    """
    Extracts relevant information from feed entries and includes FeedSpec details.
    """
    articles = []
    if not feed or not feed.entries:
        return articles

    for entry in feed.entries:
        article = {
            'title': entry.get('title', 'N/A'),
            'link': entry.get('link', 'N/A'),
            'published': entry.get('published', entry.get('updated', 'N/A')),
            'summary': entry.get('summary', entry.get('description', 'N/A')),
            'id': entry.get('id', entry.get('link', '')),

            # Original source feed info from feedparser
            'source_feed_title_raw': feed.feed.get('title', 'N/A') if feed.feed else 'N/A',
            'source_feed_url_raw': feed.href if hasattr(feed, 'href') else 'N/A',

            # Information from our FeedSpec
            'spec_publisher_id': feed_spec.publisher.id,
            'spec_publisher_name': feed_spec.publisher.name,
            'spec_title': feed_spec.title,
            'spec_url': feed_spec.url,
            'spec_categories': feed_spec.categories,
        }
        articles.append(article)
    return articles

if __name__ == '__main__':
    # This __main__ block needs adjustment if we want to test the new parse_feed_entries
    # It would require creating a dummy FeedSpec object.

    from .models import Publisher # For creating dummy FeedSpec

    # Check if dummy publisher data exists to create a somewhat realistic FeedSpec for testing
    # This is a simplified test for parse_feed_entries if run directly.
    # Full integration testing is better done via main.py.

    # Using a known public feed for testing fetch_feed
    test_feed_url_for_fetch = "http://rss.cnn.com/rss/cnn_topstories.rss"
    print(f"Testing fetch_feed with URL: {test_feed_url_for_fetch}")

    parsed_feed_content = fetch_feed(test_feed_url_for_fetch)

    if parsed_feed_content:
        print(f"Successfully fetched content for {test_feed_url_for_fetch}.")
        print(f"Feed Title (raw): {parsed_feed_content.feed.get('title', 'N/A')}")
        print(f"Number of entries: {len(parsed_feed_content.entries)}")

        # Attempt to test parse_feed_entries with a dummy FeedSpec
        print("\nAttempting to test parse_feed_entries with a dummy FeedSpec...")
        dummy_publisher = Publisher(id="p_dummy", name="Dummy Publisher", type="Test", url="http://dummy.com")
        # Use the fetched URL for the dummy spec to match the content
        dummy_spec_for_test = FeedSpec(publisher=dummy_publisher, title="Dummy Spec for CNN", url=test_feed_url_for_fetch, categories=["dummy", "test"])

        parsed_articles_with_spec = parse_feed_entries(parsed_feed_content, dummy_spec_for_test)

        if parsed_articles_with_spec:
            print(f"Successfully parsed {len(parsed_articles_with_spec)} articles with dummy spec info.")
            print("First article with spec info:")
            for key, value in parsed_articles_with_spec[0].items():
                print(f"  {key}: {value}")
        else:
            print("Could not parse articles with dummy spec info, or no entries in feed.")

    else:
        print(f"Failed to fetch or parse the feed from {test_feed_url_for_fetch}.")

    print("\nNote: Full testing of parse_feed_entries with various FeedSpec data is best done via main.py or dedicated unit tests.")
