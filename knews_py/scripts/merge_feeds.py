#!/usr/bin/env python3
# This script serves as an entry point to run the feed merging process.

import sys
import os

# Path adjustment similar to collect_feeds.py
# Adding the project root (/app) to sys.path to allow 'from knews_py.src...'
# Current file: /app/knews_py/scripts/merge_feeds.py
# Project root containing 'knews_py' package: /app
PACKAGE_PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This is /app/knews_py
# To import 'from knews_py.src...', the directory containing 'knews_py' must be in path.
# That is os.path.dirname(PACKAGE_PARENT_DIR) -> /app
if os.path.dirname(PACKAGE_PARENT_DIR) not in sys.path:
    sys.path.insert(0, os.path.dirname(PACKAGE_PARENT_DIR))

try:
    from knews_py.src.merge import merge_collected_feeds
except ModuleNotFoundError as e:
    print(f"Error: Could not import 'merge_collected_feeds' ({e}).")
    print("Ensure 'knews_py' package is correctly installed or PYTHONPATH is set.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

if __name__ == '__main__':
    print("Executing Knews feed merging via scripts/merge_feeds.py...")
    merge_collected_feeds()
    print("Feed merging script finished.")
