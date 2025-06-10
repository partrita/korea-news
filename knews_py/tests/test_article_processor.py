import unittest
from knews_py.src.article_processor import normalize_date # Adjust path as needed

class TestArticleProcessor(unittest.TestCase):

    def test_normalize_date(self):
        # Test cases adapted from Deno's parser_test.ts and common formats
        # dateutil.parser is quite flexible.
        # Output should be ISO 8601 format with UTC timezone (ending in +00:00 or Z)

        cases = {
            # Input date string : Expected ISO 8601 UTC string or None if invalid
            "2022-07-16T22:01:07+09:00": "2022-07-16T13:01:07+00:00", # KST
            "2022-07-16 13:01:07Z": "2022-07-16T13:01:07+00:00",     # Assumed UTC if Z present
            "2022-07-16 13:01:07 UTC": "2022-07-16T13:01:07+00:00",
            "Sat, 16 Jul 2022 22:01:07 +0900": "2022-07-16T13:01:07+00:00", # KST in RFC 822
            "Sat, 16 Jul 2022 13:01:07 GMT": "2022-07-16T13:01:07+00:00",
            "16 Jul 2022 13:01:07 GMT": "2022-07-16T13:01:07+00:00",

            # Ambiguous date (no timezone, dateutil might assume local or handle differently)
            # The normalize_date function assumes UTC if naive.
            "2023-01-15 10:00:00": "2023-01-15T10:00:00+00:00", # Assumed UTC by normalize_date

            # Different timezone (CEST is UTC+2)
            "Mon, 24 Apr 2023 10:00:00 +0200": "2023-04-24T08:00:00+00:00", # CEST to UTC

            # Invalid dates
            "Invalid Date": None,
            "2023-13-01T00:00:00Z": None, # Invalid month
            "": None,
            None: None, # Function expects string, testing None explicitly
        }

        for raw_date, expected_iso in cases.items():
            with self.subTest(raw_date=str(raw_date)): # Ensure raw_date is string for subtest name
                actual_iso = normalize_date(raw_date)
                self.assertEqual(actual_iso, expected_iso, f"Failed for date: {raw_date}")

if __name__ == '__main__':
    unittest.main()
