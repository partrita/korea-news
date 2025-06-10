import csv
from typing import List, Dict, Optional
from .models import Publisher, FeedSpec # Assuming models.py is in the same directory
import os

# Default paths relative to this file's location (knews_py/src/)
# So, it goes up one level to knews_py, then into data/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PUBLISHERS_PATH = os.path.join(BASE_DIR, '..', 'data', 'publishers.csv')
DEFAULT_FEED_SPECS_PATH = os.path.join(BASE_DIR, '..', 'data', 'feed_specs.csv')

def load_publishers(publishers_path: str = DEFAULT_PUBLISHERS_PATH) -> Dict[str, Publisher]:
    """Loads publishers from a CSV file into a dictionary keyed by publisher NAME."""
    publishers_by_name: Dict[str, Publisher] = {}
    try:
        with open(publishers_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pub_name = row.get('name')
                if not pub_name:
                    print(f"Skipping publisher row due to missing name: {row}")
                    continue

                # Ensure required fields are present
                pub_id = row.get('id')
                if not pub_id:
                    print(f"Skipping publisher '{pub_name}' due to missing ID.")
                    continue

                pub = Publisher(
                    id=pub_id,
                    name=pub_name,
                    type=row.get('type', ''),
                    url=row.get('url', '')
                )
                if pub_name in publishers_by_name:
                    print(f"Warning: Duplicate publisher name '{pub_name}' found. Overwriting.")
                publishers_by_name[pub_name] = pub
    except FileNotFoundError:
        print(f"Error: Publishers file not found at {publishers_path}")
        # exit(1) # Or raise an exception
    except Exception as e:
        print(f"Error loading publishers from {publishers_path}: {e}")
        # exit(1) # Or raise an exception
    return publishers_by_name

def load_feed_specs(
    feed_specs_path: str = DEFAULT_FEED_SPECS_PATH,
    publishers_path: str = DEFAULT_PUBLISHERS_PATH
) -> List[FeedSpec]:
    """Loads feed specifications from a CSV file and links them to publishers (looked up by name)."""
    publishers_map = load_publishers(publishers_path)
    feed_specs: List[FeedSpec] = []

    if not publishers_map:
        print("Cannot load feed specs as no publishers were loaded (or publisher file was empty/not found).")
        return feed_specs

    try:
        with open(feed_specs_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Expected CSV columns in feed_specs.csv: 'publisher' (name), 'title', 'categories' (pipe-separated), 'url'
            for row in reader:
                publisher_name = row.get('publisher')
                if not publisher_name:
                    print(f"Skipping feed spec row due to missing 'publisher' (name) field: {row}")
                    continue

                publisher_obj = publishers_map.get(publisher_name)
                if not publisher_obj:
                    print(f"Warning: Publisher name '{publisher_name}' from feed_specs.csv not found in loaded publishers. Skipping spec: '{row.get('title', 'N/A')}'.")
                    continue

                categories_str = row.get('categories', '')
                categories_list = [c.strip() for c in categories_str.split('|') if c.strip()] if categories_str else []

                spec_url = row.get('url')
                if not spec_url:
                    print(f"Skipping feed spec '{row.get('title', 'N/A')}' for publisher '{publisher_name}' due to missing URL.")
                    continue

                spec = FeedSpec(
                    publisher=publisher_obj,
                    title=row.get('title', 'Untitled Feed'),
                    categories=categories_list,
                    url=spec_url
                )
                feed_specs.append(spec)
    except FileNotFoundError:
        print(f"Error: Feed specs file not found at {feed_specs_path}")
        # exit(1) # Or raise an exception
    except Exception as e:
        print(f"Error loading feed specs from {feed_specs_path}: {e}")
        # exit(1) # Or raise an exception
    return feed_specs

if __name__ == '__main__':
    print("--- Testing spec_loader.py ---")

    # Test with default paths (which should point to knews_py/data/ with dummy files)
    print(f"Using default publishers path: {DEFAULT_PUBLISHERS_PATH}")
    print(f"Using default feed_specs path: {DEFAULT_FEED_SPECS_PATH}")

    # Check if dummy files exist, otherwise the test is not meaningful
    if not os.path.exists(DEFAULT_PUBLISHERS_PATH):
        print(f"TEST ERROR: Dummy publishers file {DEFAULT_PUBLISHERS_PATH} not found!")
    if not os.path.exists(DEFAULT_FEED_SPECS_PATH):
        print(f"TEST ERROR: Dummy feed_specs file {DEFAULT_FEED_SPECS_PATH} not found!")

    loaded_specs = load_feed_specs()

    if loaded_specs:
        print(f"Successfully loaded {len(loaded_specs)} feed specs:")
        for i, spec in enumerate(loaded_specs):
            print(f"  Spec {i+1}:")
            print(f"    Publisher: {spec.publisher.name} (ID: {spec.publisher.id})")
            print(f"    Title: {spec.title}")
            print(f"    Categories: {spec.categories}")
            print(f"    URL: {spec.url}")
    else:
        print("No feed specs were loaded. Check for errors above or if CSV files are empty/missing.")

    print("--- End of spec_loader.py test ---")
