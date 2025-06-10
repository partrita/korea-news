# knews_py/src/article_processor.py

from dateutil import parser as date_parser
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse # For robust domain extraction

# For HTML cleaning, you might use BeautifulSoup or a simpler regex approach
# from bs4 import BeautifulSoup # Example
# import re # Example

from .config import EXCLUDED_DOMAINS # Import excluded domains

def get_domain_from_url(url: str) -> Optional[str]:
    """Extracts the domain (e.g., example.com) from a URL."""
    if not url or not isinstance(url, str):
        return None
    try:
        return urlparse(url).netloc
    except Exception as e:
        print(f"Error parsing URL {url} to get domain: {e}")
        return None

def filter_articles_by_domain(articles: List[Dict], excluded_domains: List[str]) -> List[Dict]:
    """
    Filters out articles whose link's domain is in the excluded_domains list.
    """
    if not excluded_domains:
        return articles

    filtered_articles = []
    for article in articles:
        article_url = article.get('link')
        if not article_url:
            filtered_articles.append(article) # Keep articles with no URL for now
            continue

        domain = get_domain_from_url(article_url)
        if domain and any(excluded_domain in domain for excluded_domain in excluded_domains):
            print(f"Filtering out article from {domain}: {article.get('title', 'N/A')}")
            continue
        filtered_articles.append(article)

    return filtered_articles

def normalize_date(date_string: str) -> Optional[str]:
    """
    Parses a date string and converts it to a standard ISO 8601 format with timezone.
    Returns None if parsing fails.
    """
    if not date_string or date_string == 'N/A':
        return None
    try:
        # Parse the date using dateutil.parser
        dt = date_parser.parse(date_string)

        # If the datetime object is naive (no timezone info), assume UTC.
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Convert to UTC if it has timezone info but isn't UTC
            dt = dt.astimezone(timezone.utc)

        return dt.isoformat()
    except (ValueError, TypeError) as e:
        print(f"Could not parse date: {date_string}. Error: {e}")
        return None

def clean_html(html_content: str) -> str:
    """
    Removes HTML tags from a string.
    (Placeholder - a more robust implementation is needed, e.g., using BeautifulSoup)
    """
    if not html_content:
        return ""
    # Basic example (not robust for all HTML):
    # import re
    # clean_text = re.sub(r'<[^>]+>', '', html_content)
    # return clean_text

    # Using BeautifulSoup would be more reliable:
    # from bs4 import BeautifulSoup
    # soup = BeautifulSoup(html_content, "html.parser")
    # return soup.get_text()

    print("Warning: clean_html is using a placeholder implementation.")
    return html_content # Placeholder: returns original content

def process_articles(articles: List[Dict]) -> List[Dict]:
    """
    Processes a list of article dictionaries.
    - Filters articles by domain.
    - Normalizes publication dates.
    - Cleans HTML from summaries.
    """
    # First, filter articles by domain
    articles_after_domain_filter = filter_articles_by_domain(articles, EXCLUDED_DOMAINS)

    if len(articles) != len(articles_after_domain_filter):
        print(f"Filtered out {len(articles) - len(articles_after_domain_filter)} articles by domain.")

    processed_articles = []
    for article in articles_after_domain_filter: # Iterate over the filtered list
        processed_article = article.copy() # Work on a copy

        # Normalize 'published' date
        if 'published' in processed_article:
            processed_article['published_normalized'] = normalize_date(processed_article['published'])

        # Clean HTML from 'summary'
        if 'summary' in processed_article:
            processed_article['summary_cleaned'] = clean_html(processed_article['summary'])

        # Future processing steps can be added here:
        # - Keyword extraction
        # - Sentiment analysis
        # - Fetching full article content (if newspaper3k or similar is used)

        processed_articles.append(processed_article)

    return processed_articles

if __name__ == '__main__':
    # Example Usage:
    # Sample articles similar to what feed_parser.py would produce
    sample_articles_data = [
        {
            'title': 'Sample Article 1',
            'link': 'http://example.com/article1',
            'published': 'Tue, 20 Apr 2023 15:00:00 +0000',
            'summary': '<p>This is a <b>summary</b> with HTML.</p>',
            'id': 'tag:example.com,2023:article1',
            'source_feed_title': 'Sample Feed',
            'source_feed_url': 'http://example.com/feed',
            'link': 'http://good.example.com/article1' # Added link for domain testing
        },
        {
            'title': 'Sample Article 2 (Excluded Domain)',
            'link': 'http://khan.co.kr/article2', # This domain is in EXCLUDED_DOMAINS
            'published': '2023-04-21T10:20:30Z', # ISO format
            'summary': 'Just a plain text summary.',
            'id': 'tag:example.com,2023:article2',
            'source_feed_title': 'Sample Feed',
            'source_feed_url': 'http://example.com/feed',
        },
        {
            'title': 'Sample Article 3 (No Date, No URL)',
            'link': None, # Test case for no URL
            'published': 'N/A',
            'summary': 'Another summary.',
            'id': 'tag:example.com,2023:article3',
            'source_feed_title': 'Sample Feed',
            'source_feed_url': 'http://example.com/feed'
        },
         {
            'title': 'Sample Article 4 (CEST Date)',
            'link': 'http://anothergood.example.com/article4', # Added link
            'published': 'Mon, 24 Apr 2023 10:00:00 +0200', # CEST
            'summary': 'Summary with a different timezone.',
            'id': 'tag:example.com,2023:article4',
            'source_feed_title': 'Sample Feed',
            'source_feed_url': 'http://example.com/feed'
        }
    ]

    print(f"EXCLUDED_DOMAINS for testing: {EXCLUDED_DOMAINS}")
    print(f"Original number of sample articles: {len(sample_articles_data)}")
    print("\nProcessing sample articles...")
    processed_articles_data = process_articles(sample_articles_data)
    print(f"\nNumber of articles after processing: {len(processed_articles_data)}")


    for i, article in enumerate(processed_articles_data): # This will now iterate over filtered articles
        print(f"\n--- Remaining Article {i+1} ---")
        print(f"  Title: {article['title']}")
        print(f"  Original Published Date: {article['published']}")
        print(f"  Normalized Published Date: {article.get('published_normalized', 'N/A')}")
        print(f"  Original Summary: {article['summary']}")
        print(f"  Cleaned Summary: {article.get('summary_cleaned', 'N/A')}")

    # Test normalize_date directly
    print("\n--- Testing normalize_date ---")
    test_dates = ["Tue, 20 Apr 2023 15:00:00 +0000", "2023-04-21T10:20:30Z", "Sun, 23 Apr 2023 08:30:00 GMT", "22 April 2023 12:00", "Invalid Date", None, "N/A", "Mon, 24 Apr 2023 10:00:00 +0200"]
    for td in test_dates:
        print(f"Original: '{td}' -> Normalized: '{normalize_date(td)}'")
