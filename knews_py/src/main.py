# knews_py/src/main.py

import argparse
from . import config # Default configurations
from . import feed_parser
from . import article_processor
from . import data_writer # data_writer.py now has DEFAULT_OUTPUT_DIR
from .spec_loader import load_feed_specs
from .models import FeedSpec, Publisher # Import FeedSpec and Publisher

def run_news_aggregator(
    use_spec_files: bool = True,
    feed_urls_fallback: list = None,
    output_formats: list = None,
    output_directory: str = None,
    max_articles: int = None
):
    """
    Main function to run the news aggregation process.
    """

    specs_to_process: list[FeedSpec] = []

    if use_spec_files:
        print("Attempting to load feed specifications from CSV files...")
        loaded_specs = load_feed_specs() # Uses default paths in spec_loader
        if loaded_specs:
            specs_to_process = loaded_specs
            print(f"Loaded {len(specs_to_process)} feed specifications from files.")
        else:
            print("No feed specifications loaded from files.")
            if not feed_urls_fallback:
                print("No fallback URLs provided. Exiting.")
                return
            print("Falling back to provided/default URL list.")

    if not specs_to_process: # Fallback or if use_spec_files is False
        urls_to_use = feed_urls_fallback if feed_urls_fallback else config.DEFAULT_FEED_URLS
        if not urls_to_use:
            print("No feed URLs provided or configured, and no specs loaded. Exiting.")
            return

        unknown_publisher = Publisher(id="unknown", name="Generic Feed", type="Generic", url="")
        for url_idx, url_str in enumerate(urls_to_use):
            dummy_spec = FeedSpec(
                publisher=unknown_publisher,
                title=f"Feed from {url_str}",
                url=url_str,
                categories=[]
            )
            specs_to_process.append(dummy_spec)
        print(f"Processing {len(specs_to_process)} feeds from URL list.")

    # Set defaults for arguments if not provided
    output_formats = output_formats if output_formats is not None else ['json', 'csv', 'xml'] # Added 'xml' to defaults
    output_directory = output_directory if output_directory is not None else data_writer.DEFAULT_OUTPUT_DIR
    max_articles_per_feed = max_articles if max_articles is not None else config.MAX_ARTICLES_PER_FEED

    print(f"Output formats: {output_formats}")
    print(f"Output directory: {output_directory}")
    print(f"Max articles per feed: {max_articles_per_feed}")

    all_articles_raw = []
    for spec in specs_to_process:
        print(f"Fetching feed: {spec.publisher.name} - {spec.title} ({spec.url})")
        parsed_feed_content = feed_parser.fetch_feed(spec.url)
        if parsed_feed_content:
            articles_from_feed = feed_parser.parse_feed_entries(parsed_feed_content, spec)
            articles_from_feed = articles_from_feed[:max_articles_per_feed]
            all_articles_raw.extend(articles_from_feed)
            print(f"Fetched {len(articles_from_feed)} articles from {spec.url}.")
        else:
            print(f"Could not fetch or parse feed: {spec.url}")

    if not all_articles_raw:
        print("No articles fetched. Exiting.")
        return

    print(f"\nTotal raw articles fetched: {len(all_articles_raw)}")
    processed_articles = article_processor.process_articles(all_articles_raw)
    print(f"Total articles after processing: {len(processed_articles)}")

    data_writer.ensure_output_directory(output_directory)

    if 'json' in output_formats:
        print(f"\nWriting {len(processed_articles)} articles to JSON...")
        data_writer.write_to_json(processed_articles, "news_articles.json", directory=output_directory)

    if 'csv' in output_formats:
        print(f"\nWriting {len(processed_articles)} articles to CSV...")
        data_writer.write_to_csv(processed_articles, "news_articles.csv", directory=output_directory)

    if 'xml' in output_formats:
        print(f"\nWriting {len(processed_articles)} articles to RSS XML...")
        # Create a generic FeedSpec for the "all articles" RSS feed
        all_articles_publisher = Publisher(
            id="knews_py_aggregator",
            name="Knews-Py Aggregated Feeds",
            type="Aggregator",
            url="local://knews_py.aggregated.feed" # Placeholder URL for the aggregator itself
        )
        all_articles_spec = FeedSpec(
            publisher=all_articles_publisher,
            title="All Aggregated News",
            url="local://all_articles.xml", # Placeholder URL for the aggregated feed itself
            categories=["news", "aggregated"]
        )
        data_writer.write_to_rss_xml(
            all_articles_spec,
            processed_articles,
            "all_articles.xml", # Filename
            directory=output_directory
        )

    print("\nNews aggregation process completed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Knews Aggregator")
    parser.add_argument("--source", choices=['specs', 'urls'], default='specs', help="Source of feeds")
    parser.add_argument("--urls", nargs='+', default=None, help="List of RSS feed URLs if --source=urls")
    parser.add_argument("--formats", nargs='+', choices=['json', 'csv', 'xml'], default=['json', 'csv', 'xml'], help="Output formats") # 'xml' now default
    parser.add_argument("--output-dir", type=str, default=data_writer.DEFAULT_OUTPUT_DIR, help="Output directory") # Use constant from data_writer
    parser.add_argument("--max-articles", type=int, default=config.MAX_ARTICLES_PER_FEED, help="Max articles per feed")
    args = parser.parse_args()

    use_specs = True if args.source == 'specs' else False
    fallback_urls = args.urls if args.urls else None


    print("Running Knews Aggregator (main.py with CLI args)...")
    run_news_aggregator(
        use_spec_files=use_specs,
        feed_urls_fallback=fallback_urls,
        output_formats=args.formats,
        output_directory=args.output_dir,
        max_articles=args.max_articles
    )
