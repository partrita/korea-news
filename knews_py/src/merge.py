import json
import os
import shutil
from typing import List, Dict, Any, DefaultDict
from collections import defaultdict
from datetime import datetime, timezone # Added timezone

# Use relative imports for intra-package modules
from .data_writer import write_to_rss_xml, ensure_output_directory
from .models import FeedSpec, Publisher # For creating FeedSpec objects for XML channels

# Define paths relative to the 'knews_py' package directory
PACKAGE_ROOT_MERGE = os.path.dirname(os.path.abspath(__file__)) # /app/knews_py/src
BASE_OUTPUT_DIR_MERGE = os.path.join(PACKAGE_ROOT_MERGE, "..", "output") # /app/knews_py/output

# Input directory for JSON files (from collect.py)
COLLECTION_JSON_DIR = os.path.join(BASE_OUTPUT_DIR_MERGE, "collection_stage_json")

# Base output directory for merged XML files
MERGED_XML_BASE_DIR = os.path.join(BASE_OUTPUT_DIR_MERGE, "merged_xml")
PUBLISHERS_XML_DIR = os.path.join(MERGED_XML_BASE_DIR, "publishers")
CATEGORIES_XML_DIR = os.path.join(MERGED_XML_BASE_DIR, "categories")
ALL_XML_FILEPATH = os.path.join(MERGED_XML_BASE_DIR, "all.xml")

def sort_articles_by_date(articles: List[Dict]) -> List[Dict]:
    """Sorts articles by their 'published_normalized' date string (ISO format), most recent first."""
    def get_sort_key(article: Dict):
        date_str = article.get('published_normalized')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                # If datetime has no timezone, assume UTC (as per how normalize_date ideally works)
                if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                return datetime.min.replace(tzinfo=timezone.utc) # Ensure tzinfo for comparison
        return datetime.min.replace(tzinfo=timezone.utc)

    return sorted(articles, key=get_sort_key, reverse=True)

def merge_collected_feeds():
    """
    Reads all collected JSON article files, groups them, sorts them,
    and generates various aggregated RSS XML feeds.
    """
    print("Starting feed merging process...")

    if not os.path.exists(COLLECTION_JSON_DIR) or not os.listdir(COLLECTION_JSON_DIR):
        print(f"Collection directory {COLLECTION_JSON_DIR} is empty or does not exist. Run collect.py first.")
        return

    all_articles: List[Dict] = []
    print(f"Reading JSON files from {COLLECTION_JSON_DIR}...")
    for filename in os.listdir(COLLECTION_JSON_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(COLLECTION_JSON_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    articles_from_file = json.load(f)
                    all_articles.extend(articles_from_file)
                    print(f"Loaded {len(articles_from_file)} articles from {filename}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {filename}. Skipping.")
            except Exception as e:
                print(f"Error reading file {filename}: {e}. Skipping.")

    if not all_articles:
        print("No articles loaded from JSON files. Exiting merge process.")
        return

    print(f"Total articles loaded: {len(all_articles)}")

    all_articles = sort_articles_by_date(all_articles)
    print("All articles sorted by date.")

    ensure_output_directory(MERGED_XML_BASE_DIR)
    ensure_output_directory(PUBLISHERS_XML_DIR)
    ensure_output_directory(CATEGORIES_XML_DIR)

    print(f"Saving all {len(all_articles)} articles to {ALL_XML_FILEPATH}...")
    generic_publisher_all = Publisher(id="knews_aggregator", name="Knews Aggregated", type="Aggregator", url="")
    generic_spec_all = FeedSpec(
        publisher=generic_publisher_all,
        title="All Knews Feeds",
        url="local://all.xml",
        categories=["all"]
    )
    write_to_rss_xml(generic_spec_all, all_articles, os.path.basename(ALL_XML_FILEPATH), MERGED_XML_BASE_DIR)

    print("Grouping articles by publisher...")
    feeds_by_publisher: DefaultDict[str, List[Dict]] = defaultdict(list)
    for article in all_articles:
        pub_id = article.get('spec_publisher_id')
        if isinstance(pub_id, str) and pub_id:
            feeds_by_publisher[pub_id].append(article)

    print(f"Found {len(feeds_by_publisher)} publishers. Saving XML for each...")
    for publisher_id, articles_for_publisher in feeds_by_publisher.items():
        if not articles_for_publisher: continue

        first_article = articles_for_publisher[0]
        publisher_obj = Publisher(
            id=first_article.get('spec_publisher_id', publisher_id),
            name=first_article.get('spec_publisher_name', 'Unknown Publisher'),
            type="Feed Collection",
            url=first_article.get('spec_url', '')
        )
        publisher_feed_spec = FeedSpec(
            publisher=publisher_obj,
            title=f"{publisher_obj.name} - Collected Feeds",
            url=publisher_obj.url,
            categories=first_article.get('spec_categories', [])
        )

        filename = f"{publisher_id}.xml" # Publisher IDs are typically safe for filenames
        print(f"Saving {len(articles_for_publisher)} articles for publisher {publisher_id} to {os.path.join(PUBLISHERS_XML_DIR, filename)}...")
        write_to_rss_xml(publisher_feed_spec, articles_for_publisher, filename, PUBLISHERS_XML_DIR)

    print("Grouping articles by category...")
    feeds_by_category: DefaultDict[str, List[Dict]] = defaultdict(list)
    for article in all_articles:
        categories = article.get('spec_categories', [])
        if isinstance(categories, list):
            for category_name in categories:
                if isinstance(category_name, str) and category_name:
                    feeds_by_category[category_name].append(article)

    print(f"Found {len(feeds_by_category)} categories. Saving XML for each...")
    for category_name, articles_for_category in feeds_by_category.items():
        if not articles_for_category: continue

        category_publisher_obj = Publisher(
            id=f"category_{category_name.lower().replace(' ', '_').replace('/', '_')}",
            name=f"Knews Category: {category_name}",
            type="Category Feed",
            url=""
        )
        category_feed_spec = FeedSpec(
            publisher=category_publisher_obj,
            title=f"Articles in Category: {category_name}",
            url="",
            categories=[category_name]
        )

        safe_category_filename = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in category_name).lower() + ".xml"
        if not safe_category_filename.replace('_','').replace('.xml',''):
            safe_category_filename = f"category_fallback_{len(feeds_by_category)}.xml"

        print(f"Saving {len(articles_for_category)} articles for category '{category_name}' to {os.path.join(CATEGORIES_XML_DIR, safe_category_filename)}...")
        write_to_rss_xml(category_feed_spec, articles_for_category, safe_category_filename, CATEGORIES_XML_DIR)

    print("Feed merging process completed.")

if __name__ == '__main__':
    if os.path.exists(MERGED_XML_BASE_DIR):
        print(f"Cleaning up previous merge output directory: {MERGED_XML_BASE_DIR}")
        shutil.rmtree(MERGED_XML_BASE_DIR)

    print("Running merge_collected_feeds() directly...")
    merge_collected_feeds()
    print(f"\nCheck the '{MERGED_XML_BASE_DIR}' directory and its subdirectories for output XML files.")

    print(f"\nFiles in {MERGED_XML_BASE_DIR}:")
    try:
        for item in os.listdir(MERGED_XML_BASE_DIR): print(f"- {item}")
    except FileNotFoundError: print(f"Directory not found: {MERGED_XML_BASE_DIR}")

    if os.path.exists(PUBLISHERS_XML_DIR):
        print(f"\nFiles in {PUBLISHERS_XML_DIR}:")
        try:
            for item in os.listdir(PUBLISHERS_XML_DIR): print(f"- {item}")
        except FileNotFoundError: print(f"Directory not found: {PUBLISHERS_XML_DIR}")

    if os.path.exists(CATEGORIES_XML_DIR):
        print(f"\nFiles in {CATEGORIES_XML_DIR}:")
        try:
            for item in os.listdir(CATEGORIES_XML_DIR): print(f"- {item}")
        except FileNotFoundError: print(f"Directory not found: {CATEGORIES_XML_DIR}")
