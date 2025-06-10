import csv
import io
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python process_urls.py \"<csv_data_string>\"")
        sys.exit(1) # Exit if not enough arguments

    csv_data = sys.argv[1]

    # Use io.StringIO to treat the string as a file
    csvfile = io.StringIO(csv_data)
    reader = csv.DictReader(csvfile)

    for row in reader:
        if 'url' in row:
            print(row['url'])

if __name__ == "__main__":
    main()
