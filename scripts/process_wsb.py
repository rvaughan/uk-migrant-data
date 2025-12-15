"""
Simple script for processing the UK Government's weekly small boat data.

The data source is now:
https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats/weekly-summary-of-small-boat-arrivals-and-preventions

The page contains:
- A heading with the week ending date (e.g., "Week ending 7 December 2025")
- A table with columns: Migrants arrived, Boats arrived, Migrants prevented, Events prevented

Note: The old format provided daily breakdowns within each week. The new format
only provides weekly aggregate data. The CSV format has been updated to reflect this:
week_ending_date,migrants_arrived,boats_arrived,migrants_prevented,events_prevented
"""
import csv
import os
import re
import sys
from datetime import datetime

from bs4 import BeautifulSoup


if len(sys.argv) < 3:
    print('Usage: process_wsb.py <input_file> <output_file>')
    sys.exit(-1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Read existing week ending dates from CSV to avoid duplicates
existing_weeks = set()
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and not row[0].startswith('#'):
                existing_weeks.add(row[0].strip('"'))

# Parse the HTML file
with open(input_file, 'r') as f:
    html = BeautifulSoup(f, features="html.parser")

    # Find the week ending date from headings
    week_ending_date = None
    headings = html.find_all(['h2', 'h3'])
    for heading in headings:
        text = heading.text.strip()
        # Match "Week ending 7 December 2025" pattern
        match = re.search(r'Week ending (\d{1,2} \w+ \d{4})', text)
        if match:
            try:
                dt = datetime.strptime(match.group(1), '%d %B %Y')
                week_ending_date = dt.strftime('%Y-%m-%d')
                break
            except ValueError:
                continue

    if not week_ending_date:
        print('Could not find week ending date in the HTML')
        sys.exit(1)

    if week_ending_date in existing_weeks:
        print(f'Week ending {week_ending_date} already exists in CSV')
        sys.exit(0)

    # Find the data table
    tables = html.find_all('table')

    data_found = False
    for table in tables:
        rows = table.find_all('tr')
        # Look for the data row (skip header row)
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                try:
                    # Get the four values: migrants arrived, boats arrived,
                    # migrants prevented, events prevented
                    migrants_arrived = cells[0].text.strip().replace(',', '')
                    boats_arrived = cells[1].text.strip().replace(',', '')
                    migrants_prevented = cells[2].text.strip().replace(',', '')
                    events_prevented = cells[3].text.strip().replace(',', '')

                    # Handle non-numeric values
                    migrants_arrived = int(migrants_arrived) if migrants_arrived.isdigit() else 0
                    boats_arrived = int(boats_arrived) if boats_arrived.isdigit() else 0
                    migrants_prevented = int(migrants_prevented) if migrants_prevented.isdigit() else 0
                    events_prevented = int(events_prevented) if events_prevented.isdigit() else 0

                    # Append to CSV
                    with open(output_file, 'a') as of:
                        of.write(f'"{week_ending_date}",{migrants_arrived},{boats_arrived},{migrants_prevented},{events_prevented}\n')

                    print(f'Added week ending {week_ending_date}: {migrants_arrived} migrants, {boats_arrived} boats')
                    data_found = True
                    break
                except (ValueError, AttributeError) as e:
                    continue

        if data_found:
            break

    if not data_found:
        print('Could not find data in the HTML')
