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

This script reads the "last 7 days" HTML page and updates the CSV file.
It will add new entries and update existing entries if the new data has
higher values (the live data is more current than the ODS time series).
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

# Read existing data from CSV
existing_data = {}
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and not row[0].startswith('#'):
                date_str = row[0].strip('"')
                migrants = int(row[1])
                boats = int(row[2])
                existing_data[date_str] = (migrants, boats)

# Parse the HTML file
updates = []
with open(input_file, 'r') as f:
    html = BeautifulSoup(f, features="html.parser")

    # Find the data table - look for tables with date/migrants/boats structure
    tables = html.find_all('table')

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

                    # Check if this is new or an update
                    if date_str not in existing_data:
                        existing_data[date_str] = (migrants, boats)
                        updates.append(f'Added {date_str}: {migrants} migrants, {boats} boats')
                    elif existing_data[date_str] != (migrants, boats):
                        old_migrants, old_boats = existing_data[date_str]
                        existing_data[date_str] = (migrants, boats)
                        updates.append(f'Updated {date_str}: {old_migrants}->{migrants} migrants, {old_boats}->{boats} boats')
                except (ValueError, AttributeError) as e:
                    # Skip rows that don't match expected format
                    continue

# Write all data back to CSV (sorted by date)
with open(output_file, 'w') as f:
    f.write('#date,migrants,boats\n')
    for date_str in sorted(existing_data.keys()):
        migrants, boats = existing_data[date_str]
        f.write(f'"{date_str}",{migrants},{boats}\n')

if updates:
    for update in updates:
        print(update)
    print(f'Total: {len(updates)} changes')
else:
    print('No changes needed')
