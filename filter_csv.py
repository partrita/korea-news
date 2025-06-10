import csv
import io
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python filter_csv.py \"<csv_data_string>\"", file=sys.stderr)
        sys.exit(1)

    csv_data = sys.argv[1]
    domains_to_filter_out = [
        "khan.co.kr",
        "rss.kmib.co.kr",
        "ddanzi.com",
        "mediatoday.co.kr"
    ]

    # Use io.StringIO to treat the string as a file for reading
    csvfile_in = io.StringIO(csv_data)
    reader = csv.DictReader(csvfile_in)

    # Store filtered rows
    filtered_rows = []

    # Ensure the header is captured
    header = reader.fieldnames
    if header:
        filtered_rows.append(header)

    for row in reader:
        url = row.get('url', '')
        if not any(domain in url for domain in domains_to_filter_out):
            # Append the row as a list of values in the correct order
            if header:
                filtered_rows.append([row[field] for field in header])

    # Use io.StringIO to build the output CSV string
    csvfile_out = io.StringIO()
    writer = csv.writer(csvfile_out)
    writer.writerows(filtered_rows)

    print(csvfile_out.getvalue())

if __name__ == "__main__":
    main()
