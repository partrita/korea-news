# knews_py/src/data_writer.py

import json
import csv
import os
from typing import List, Dict, Any
from lxml import etree # Using lxml for XML generation
from datetime import datetime, timezone # Added timezone
from email.utils import format_datetime # For RFC-822 date format
from .models import FeedSpec # To use FeedSpec for channel metadata

# Default output directory, can be overridden
DEFAULT_OUTPUT_DIR = "output_data"

def ensure_output_directory(directory: str = DEFAULT_OUTPUT_DIR):
    """Ensures the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created output directory: {directory}")

def write_to_json(articles: List[Dict], filename: str, directory: str = DEFAULT_OUTPUT_DIR):
    """Writes a list of article dictionaries to a JSON file."""
    ensure_output_directory(directory)
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print(f"Successfully wrote {len(articles)} articles to {filepath}")
    except IOError as e:
        print(f"Error writing to JSON file {filepath}: {e}")
    except TypeError as e:
        print(f"Error serializing data to JSON for {filepath}: {e}")

def write_to_csv(articles: List[Dict], filename: str, directory: str = DEFAULT_OUTPUT_DIR):
    """Writes a list of article dictionaries to a CSV file."""
    ensure_output_directory(directory)
    filepath = os.path.join(directory, filename)

    # Define common fields. New spec fields can be added here.
    fieldnames = [
        'id', 'title', 'link', 'published', 'published_normalized',
        'summary', 'summary_cleaned',
        'spec_publisher_id', 'spec_publisher_name', 'spec_title',
        'spec_url', 'spec_categories', # Added spec fields
        'source_feed_title_raw', 'source_feed_url_raw' # Raw source info
    ]

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for article in articles:
                # Convert list of categories to a string for CSV
                article_copy = article.copy() # Work on a copy to avoid modifying original dict
                if 'spec_categories' in article_copy and isinstance(article_copy['spec_categories'], list):
                    article_copy['spec_categories'] = '|'.join(article_copy['spec_categories'])
                writer.writerow(article_copy)
        print(f"Successfully wrote {len(articles)} articles to {filepath}")
    except IOError as e:
        print(f"Error writing to CSV file {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing for {filepath}: {e}")

def write_to_rss_xml(feed_spec: FeedSpec, articles: List[Dict], filename: str, directory: str = DEFAULT_OUTPUT_DIR):
    """
    Writes a list of article dictionaries to an RSS XML file.
    Uses the provided FeedSpec for channel-level metadata.
    """
    ensure_output_directory(directory)
    filepath = os.path.join(directory, filename)

    # Define namespaces
    NSMAP = {
        'content': "http://purl.org/rss/1.0/modules/content/",
        'dc': "http://purl.org/dc/elements/1.1/"
    }

    rss_element = etree.Element("rss", version="2.0", nsmap=NSMAP)
    channel_element = etree.SubElement(rss_element, "channel")

    # Channel metadata from FeedSpec
    etree.SubElement(channel_element, "title").text = f"{feed_spec.publisher.name} - {feed_spec.title}"
    etree.SubElement(channel_element, "link").text = feed_spec.url # Link to the original feed URL or publisher site
    etree.SubElement(channel_element, "description").text = f"Aggregated feed for {feed_spec.publisher.name} - {feed_spec.title}"
    etree.SubElement(channel_element, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc)) # RFC-822 format, ensure timezone

    # Add items
    for article_data in articles:
        item_element = etree.SubElement(channel_element, "item")

        etree.SubElement(item_element, "title").text = article_data.get('title', 'N/A')
        item_link = article_data.get('link', '')
        etree.SubElement(item_element, "link").text = item_link

        guid_element = etree.SubElement(item_element, "guid", isPermaLink="true" if item_link else "false")
        guid_element.text = item_link if item_link else article_data.get('id', '')

        pub_date_iso = article_data.get('published_normalized')
        if pub_date_iso:
            try:
                # Ensure the datetime object is timezone-aware, assuming UTC if 'Z' or no offset
                dt_object = datetime.fromisoformat(pub_date_iso.replace('Z', '+00:00'))
                if dt_object.tzinfo is None: # If still naive after replace (e.g. no Z, no offset)
                    dt_object = dt_object.replace(tzinfo=timezone.utc) # Assume UTC
                else: # If it has offset, convert to UTC
                    dt_object = dt_object.astimezone(timezone.utc)

                etree.SubElement(item_element, "pubDate").text = format_datetime(dt_object)
            except ValueError:
                print(f"Warning: Could not parse date '{pub_date_iso}' for XML pubDate. Skipping pubDate for article: {article_data.get('title')}")

        summary_cleaned = article_data.get('summary_cleaned', '') # Should use summary_cleaned
        if summary_cleaned:
             # Using 'description' for basic summary, 'content:encoded' for full HTML if available
             etree.SubElement(item_element, "description").text = etree.CDATA(summary_cleaned if len(summary_cleaned) < 200 else summary_cleaned[:200] + "...") # Basic summary in description
             content_encoded = etree.SubElement(item_element, etree.QName(NSMAP['content'], 'encoded'))
             content_encoded.text = etree.CDATA(summary_cleaned) # Full summary_cleaned in content:encoded

    try:
        tree = etree.ElementTree(rss_element)
        tree.write(filepath, pretty_print=True, xml_declaration=True, encoding='utf-8')
        print(f"Successfully wrote {len(articles)} articles to RSS XML file: {filepath}")
    except IOError as e:
        print(f"Error writing to XML file {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during XML writing for {filepath}: {e}")


if __name__ == '__main__':
    print("Testing data_writer.py...")
    from .models import Publisher # Relative import for models

    dummy_publisher = Publisher(id="pub_all", name="All Knews Feeds", type="Aggregation", url="https://github.com/akngs/knews-rss")
    dummy_feed_spec_all = FeedSpec(
        publisher=dummy_publisher,
        title="Combined Feed",
        url="local://all.xml",
        categories=["all", "news"]
    )

    sample_articles_for_xml = [
        {
            'id': 'guid1', 'title': 'XML Article 1', 'link': 'http://example.com/xml/1',
            'published': '2023-04-25T10:00:00+00:00', 'published_normalized': '2023-04-25T10:00:00+00:00',
            'summary': 'Summary for XML article 1.', 'summary_cleaned': '<p>Summary for <b>XML</b> article 1.</p>',
            'spec_publisher_name': 'Test Publisher', 'spec_title': 'Test XML Feed',
            'spec_categories': ['test', 'xml']
        },
        {
            'id': 'guid2', 'title': 'XML Article 2', 'link': 'http://example.com/xml/2',
            'published': '2023-04-24T12:30:00Z', 'published_normalized': '2023-04-24T12:30:00+00:00',
            'summary': 'Summary for XML article 2, no HTML.', 'summary_cleaned': 'Summary for XML article 2, no HTML.',
            'spec_publisher_name': 'Another Publisher', 'spec_title': 'Another XML Feed',
            'spec_categories': ['general']
        },
        { # Article with potentially problematic date for testing
            'id': 'guid3', 'title': 'XML Article 3 (Bad Date)', 'link': 'http://example.com/xml/3',
            'published': 'Not A Date', 'published_normalized': None, # Simulate failed normalization
            'summary': 'Summary for XML article 3.', 'summary_cleaned': 'Summary for XML article 3.'
        }
    ]

    test_output_dir = "test_output_data_writer_xml"

    write_to_json(sample_articles_for_xml, "articles.json", directory=test_output_dir)
    write_to_csv(sample_articles_for_xml, "articles.csv", directory=test_output_dir)
    write_to_rss_xml(dummy_feed_spec_all, sample_articles_for_xml, "all_articles_rss.xml", directory=test_output_dir)

    print(f"\nCheck the '{test_output_dir}' directory for output files (json, csv, xml).")
