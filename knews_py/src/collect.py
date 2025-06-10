import time
import json
import os
import random # For sleep, or can use index-based as in original
from typing import List, Dict

# Assuming knews_py is in PYTHONPATH or script is run from project root.
# For direct execution (python src/collect.py), Python adds script's dir to path,
# so relative imports like from .spec_loader work.
# For module execution (python -m src.collect), it also works.
from .spec_loader import load_feed_specs
from .feed_parser import fetch_feed, parse_feed_entries
from .models import FeedSpec # Not strictly needed in this file if only passing spec obj

# Define output directory for the JSON files from this collection step
# Output will be inside the 'knews_py' package directory, e.g., knews_py/output/collection_stage_json
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__)) # /app/knews_py/src
COLLECTION_JSON_DIR = os.path.join(PACKAGE_ROOT, "..", "output", "collection_stage_json")

def collect_all_feeds():
    """
    Loads feed specifications, fetches articles for each spec,
    and saves them into individual JSON files.
    """
    print("Starting feed collection process...")

    feed_specs = load_feed_specs() # Uses default paths in spec_loader
    if not feed_specs:
        print("No feed specifications loaded. Exiting collection process.")
        return

    print(f"Loaded {len(feed_specs)} feed specifications.")

    try:
        if not os.path.exists(COLLECTION_JSON_DIR):
            os.makedirs(COLLECTION_JSON_DIR)
            print(f"Created directory for collected JSONs: {COLLECTION_JSON_DIR}")
    except OSError as e:
        print(f"Error creating directory {COLLECTION_JSON_DIR}: {e}")
        return

    for i, spec in enumerate(feed_specs):
        print(f"Processing spec {i+1}/{len(feed_specs)}: {spec.publisher.name} - {spec.title} ({spec.url})")
        try:
            delay = 1 + (i % 3) # Original was 1 + i % 5, reducing max delay slightly
            print(f"Sleeping for {delay} seconds...")
            time.sleep(delay)

            raw_feed_content = fetch_feed(spec.url)
            if not raw_feed_content:
                print(f"Failed to fetch feed for spec: {spec.title}. Skipping.")
                continue

            articles: List[Dict] = parse_feed_entries(raw_feed_content, spec)
            if not articles:
                print(f"No articles found or parsed for spec: {spec.title}. Skipping.")
                continue

            # Construct filename: publisher.id-category1-category2.json
            safe_categories = [cat.replace(os.sep, '_').replace('/', '_') for cat in spec.categories] # Sanitize
            categories_str = "-".join(safe_categories) if safe_categories else "general"

            # Sanitize publisher ID for filename (though less likely to have special chars)
            safe_publisher_id = spec.publisher.id.replace(os.sep, '_').replace('/', '_')
            filename = f"{safe_publisher_id}-{categories_str}.json"
            filepath = os.path.join(COLLECTION_JSON_DIR, filename)

            print(f"Writing {len(articles)} articles to {filepath}...")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=4)
            print(f"Successfully wrote articles for spec: {spec.title} to {filepath}")

        except Exception as e:
            print(f"An error occurred while processing spec {spec.title}: {e}")
            # Continue to the next spec

    print("Feed collection process completed.")

if __name__ == '__main__':
    # This makes collect.py runnable as a script
    # Ensure dummy CSVs (publishers.csv, feed_specs.csv with LIVE URLs)
    # are in knews_py/data/ for this to work.
    # The dummy data created in previous steps should work if URLs are live.

    print("Running collect_all_feeds() directly from __main__...")
    collect_all_feeds()
    print(f"\nCheck the '{COLLECTION_JSON_DIR}' directory for output files.")

    if os.path.exists(COLLECTION_JSON_DIR):
        print(f"Files in {COLLECTION_JSON_DIR}:")
        try:
            for item in os.listdir(COLLECTION_JSON_DIR):
                print(f"- {item}")
        except Exception as e:
            print(f"Error listing files in {COLLECTION_JSON_DIR}: {e}")
    else:
        print(f"Directory {COLLECTION_JSON_DIR} was not created.")
