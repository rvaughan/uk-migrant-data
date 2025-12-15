"""
Simple script for processing the UK Government's small boat data.

The data source is now:
https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats/migrants-detected-crossing-the-english-channel-in-small-boats-last-7-days

The page contains a table with columns:
- Date (in th scope="row")
- Migrants arrived
- Boats arrived
- Boats involved in uncontrolled landings
- Notes
"""
import csv
import os
import sys
from datetime import datetime

from bs4 import BeautifulSoup


if len(sys.argv) < 3:
    print('Usage: process_dsb.py <input_file> <output_file>')
    sys.exit(-1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Read existing dates from CSV to avoid duplicates
existing_dates = set()
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and not row[0].startswith('#'):
                existing_dates.add(row[0].strip('"'))

# Parse the HTML file
with open(input_file, 'r') as f:
    html = BeautifulSoup(f, features="html.parser")

    # Find the data table - look for tables with date/migrants/boats structure
    tables = html.find_all('table')

    new_entries = []

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            # Date is in th with scope="row", data is in td elements
            date_cell = row.find('th', attrs={'scope': 'row'})
            data_cells = row.find_all('td')

            if date_cell and len(data_cells) >= 2:
                try:
                    # Parse date like "13 December 2025"
                    date_text = date_cell.text.strip()
                    dt = datetime.strptime(date_text, '%d %B %Y')
                    date_str = dt.strftime('%Y-%m-%d')

                    # Get migrants and boats (first two td cells)
                    migrants = data_cells[0].text.strip().replace(',', '')
                    boats = data_cells[1].text.strip().replace(',', '')

                    # Handle non-numeric values (e.g., "-" or empty)
                    migrants = int(migrants) if migrants.isdigit() else 0
                    boats = int(boats) if boats.isdigit() else 0

                    if date_str not in existing_dates:
                        new_entries.append((date_str, migrants, boats))
                        existing_dates.add(date_str)
                except (ValueError, AttributeError) as e:
                    # Skip rows that don't match expected format
                    continue

# Append new entries to CSV
if new_entries:
    with open(output_file, 'a') as f:
        for date_str, migrants, boats in new_entries:
            f.write(f'"{date_str}",{migrants},{boats}\n')
    print(f'Added {len(new_entries)} new entries')
else:
    print('No new entries to add')
