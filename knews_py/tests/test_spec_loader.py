import unittest
import io
import os # Added for os.remove
from typing import Dict, List

# Adjust import path based on how tests will be run.
# If run with 'python -m unittest discover knews_py.tests' from project root,
# or if knews_py is in PYTHONPATH:
from knews_py.src.models import Publisher, FeedSpec
from knews_py.src.spec_loader import load_publishers, load_feed_specs

# If tests are run directly from knews_py/tests/ and src is a sibling:
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
# from src.models import Publisher, FeedSpec
# from src.spec_loader import load_publishers, load_feed_specs


class TestSpecLoader(unittest.TestCase):

    def test_load_publishers_from_string(self):
        # Simulate CSV content from a string by writing to a temporary file
        dummy_publishers_content = (
            "id,name,type,url\n"
            "id0,PubZero,News,https://zero.com\n"
            "id1,PubOne,Blog,https://one.com\n"
            "id2,PubTwo,,https://two.com\n" # Missing type
            "id3,PubThree,Magazine,\n"     # Missing URL
            "id4,PubOne,Duplicate,https://one-dup.com\n" # Duplicate name, should warn and overwrite
        )
        tmp_publishers_path = "test_temp_publishers.csv"
        with open(tmp_publishers_path, "w", encoding="utf-8") as f:
            f.write(dummy_publishers_content)

        expected_publishers: Dict[str, Publisher] = {
            "PubZero": Publisher(id="id0", name="PubZero", type="News", url="https://zero.com"),
            "PubOne": Publisher(id="id4", name="PubOne", type="Duplicate", url="https://one-dup.com"), # Last one wins
            "PubTwo": Publisher(id="id2", name="PubTwo", type="", url="https://two.com"),
            "PubThree": Publisher(id="id3", name="PubThree", type="Magazine", url=""),
        }

        actual_publishers = load_publishers(publishers_path=tmp_publishers_path)

        self.assertEqual(len(actual_publishers), len(expected_publishers))
        for name, expected_pub in expected_publishers.items():
            self.assertIn(name, actual_publishers)
            self.assertEqual(actual_publishers[name], expected_pub)

        os.remove(tmp_publishers_path) # Clean up

    def test_load_feed_specs_from_string(self):
        dummy_publishers_content = (
            "id,name,type,url\n"
            "pub_id_news,News Publisher,News,https://newspub.com\n"
            "pub_id_blog,Blog Publisher,Blog,https://blogpub.com\n"
        )
        tmp_publishers_path = "test_temp_publishers_for_specs.csv"
        with open(tmp_publishers_path, "w", encoding="utf-8") as f:
            f.write(dummy_publishers_content)

        # This map is for defining expected FeedSpec objects, not directly passed to load_feed_specs
        publishers_map_for_expected: Dict[str, Publisher] = {
            "News Publisher": Publisher(id="pub_id_news", name="News Publisher", type="News", url="https://newspub.com"),
            "Blog Publisher": Publisher(id="pub_id_blog", name="Blog Publisher", type="Blog", url="https://blogpub.com"),
        }

        dummy_feed_specs_content = (
            "publisher,title,categories,url\n"
            "News Publisher,Top Stories,General|Current Events,https://newspub.com/rss/top\n"
            "News Publisher,Sports,Sports|Local,https://newspub.com/rss/sports\n"
            "Blog Publisher,Tech Thoughts,Technology|Opinion,https://blogpub.com/feed.xml\n"
            "Unknown Publisher,Lost Feed,,https://unknown.com/rss\n" # This publisher is not in publishers_map
            "News Publisher,Feed Without URL,News,\n" # This feed has no URL
        )
        tmp_feed_specs_path = "test_temp_feed_specs.csv"
        with open(tmp_feed_specs_path, "w", encoding="utf-8") as f:
            f.write(dummy_feed_specs_content)

        expected_feed_specs: List[FeedSpec] = [
            FeedSpec(publisher=publishers_map_for_expected["News Publisher"], title="Top Stories", url="https://newspub.com/rss/top", categories=["General", "Current Events"]),
            FeedSpec(publisher=publishers_map_for_expected["News Publisher"], title="Sports", url="https://newspub.com/rss/sports", categories=["Sports", "Local"]),
            FeedSpec(publisher=publishers_map_for_expected["Blog Publisher"], title="Tech Thoughts", url="https://blogpub.com/feed.xml", categories=["Technology", "Opinion"]),
        ]

        actual_feed_specs = load_feed_specs(
            feed_specs_path=tmp_feed_specs_path,
            publishers_path=tmp_publishers_path
        )

        self.assertEqual(len(actual_feed_specs), len(expected_feed_specs))
        # For dataclasses, direct list comparison should work if __eq__ is default and order is same
        self.assertListEqual(actual_feed_specs, expected_feed_specs)

        os.remove(tmp_publishers_path)
        os.remove(tmp_feed_specs_path)

if __name__ == '__main__':
    unittest.main()
