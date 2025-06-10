#!/usr/bin/env python3
# This script serves as an entry point to run the feed collection process.

import sys
import os

# Adjust sys.path to allow importing from knews_py.src
# This assumes the script is in knews_py/scripts/
# The goal is to add the directory containing 'knews_py' (i.e., the project root) to sys.path.
# os.path.abspath(__file__) -> /app/knews_py/scripts/collect_feeds.py
# os.path.dirname(os.path.abspath(__file__)) -> /app/knews_py/scripts
# os.path.dirname(os.path.dirname(os.path.abspath(__file__))) -> /app/knews_py (this is the package dir)
# We need parent of 'knews_py' package dir, which is /app
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if the intended project root (parent of knews_py package) is in sys.path
# This is usually the case if running from /app or if /app is in PYTHONPATH
# If KNEWS_PY_DIR (package dir) is what needs to be in path for 'from src...' style imports, that's different.
# Let's assume 'from knews_py.src...' is the target.
# For that, the directory *containing* 'knews_py' must be in sys.path.
# So, if KNEWS_PY_DIR = /app/knews_py, its parent is /app.
# sys.path.insert(0, KNEWS_PY_DIR) # This would be for 'from src...' if CWD is knews_py
# sys.path.insert(0, os.path.dirname(KNEWS_PY_DIR)) # This adds /app to path

# Correct path adjustment: add the directory that *contains* the 'knews_py' package.
# This is /app if the script is /app/knews_py/scripts/collect_feeds.py
# So, KNEWS_PY_PACKAGE_PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# This is getting overly complex. The standard is that the user's environment (PYTHONPATH)
# or how they invoke the script (e.g., python -m) handles this.
# For a simple script wrapper, let's assume the environment is somewhat set up,
# or rely on a simpler adjustment.

# Path adjustment: Add the 'src' directory to sys.path for direct execution.
# This allows `from collect import collect_all_feeds` if this script is moved to `src`
# or `from src.collect import collect_all_feeds` if `knews_py` is the CWD.

# Let's simplify the path logic for the script wrapper.
# Assume that when this script is run, 'knews_py' is the current working directory OR
# the knews_py package is installed / in PYTHONPATH.
# The most robust way for a script inside a package to import its own modules
# is often to run the script as a module from the parent directory, e.g.,
# python -m knews_py.scripts.collect_feeds
# However, for direct execution (./knews_py/scripts/collect_feeds.py),
# sys.path manipulation is common.

# Adding the project root (/app) to sys.path to allow 'from knews_py.src...'
# Current file: /app/knews_py/scripts/collect_feeds.py
# Project root containing 'knews_py' package: /app
# Path to add: os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) is /app
# No, this is one level too high.
# KNEWS_PY_PACKAGE_DIR is os.path.dirname(os.path.dirname(os.path.abspath(__file__))) -> /app/knews_py
# We need its parent: os.path.dirname(KNEWS_PY_PACKAGE_DIR) -> /app

PACKAGE_PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This is /app/knews_py
# To import 'from knews_py.src...', the directory containing 'knews_py' must be in path.
# That is os.path.dirname(PACKAGE_PARENT_DIR) -> /app
if os.path.dirname(PACKAGE_PARENT_DIR) not in sys.path:
    sys.path.insert(0, os.path.dirname(PACKAGE_PARENT_DIR))


try:
    from knews_py.src.collect import collect_all_feeds
except ModuleNotFoundError as e:
    print(f"Error: Could not import 'collect_all_feeds' ({e}).")
    print("Ensure 'knews_py' package is correctly installed or PYTHONPATH is set.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)


if __name__ == '__main__':
    print("Executing Knews feed collection via scripts/collect_feeds.py...")
    collect_all_feeds()
    print("Feed collection script finished.")
