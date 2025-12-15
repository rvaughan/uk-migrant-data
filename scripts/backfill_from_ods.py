"""
Script to backfill daily and weekly small boat data from the official ODS time series.

The ODS file can be downloaded from:
https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats

Usage:
    python backfill_from_ods.py <ods_file> <daily_csv> <weekly_csv>

This will:
1. Read the SB_01 sheet (daily data) and update daily_csv
2. Read the SB_02 sheet (weekly data) and update weekly_csv
"""
import csv
import sys
from datetime import datetime

import pandas as pd


def backfill_daily(ods_file, daily_csv):
    """Backfill daily data from ODS SB_01 sheet."""
    # Read ODS file
    df = pd.read_excel(ods_file, engine='odf', sheet_name='SB_01')
    df['Date'] = pd.to_datetime(df['Date'])

    # Read existing CSV to preserve any data not in ODS
    existing_data = {}
    try:
        with open(daily_csv, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and not row[0].startswith('#'):
                    date_str = row[0].strip('"')
                    existing_data[date_str] = row
    except FileNotFoundError:
        pass

    # Update with ODS data
    updated_count = 0
    added_count = 0

    for _, row in df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        migrants = int(row['Migrants arrived']) if pd.notna(row['Migrants arrived']) else 0
        boats = int(row['Boats arrived']) if pd.notna(row['Boats arrived']) else 0

        if date_str in existing_data:
            old_migrants = int(existing_data[date_str][1])
            old_boats = int(existing_data[date_str][2])
            if old_migrants != migrants or old_boats != boats:
                updated_count += 1
        else:
            added_count += 1

        existing_data[date_str] = [f'"{date_str}"', str(migrants), str(boats)]

    # Write back sorted by date
    with open(daily_csv, 'w') as f:
        f.write('#date,migrants,boats\n')
        for date_str in sorted(existing_data.keys()):
            row = existing_data[date_str]
            f.write(f'{row[0]},{row[1]},{row[2]}\n')

    print(f'Daily data: {updated_count} updated, {added_count} added, {len(existing_data)} total')


def backfill_weekly(ods_file, weekly_csv):
    """Backfill weekly data from ODS SB_02 sheet."""
    # Read ODS file
    df = pd.read_excel(ods_file, engine='odf', sheet_name='SB_02')
    df['Week ending'] = pd.to_datetime(df['Week ending'])

    # Read existing CSV
    existing_data = {}
    try:
        with open(weekly_csv, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and not row[0].startswith('#'):
                    date_str = row[0].strip('"')
                    existing_data[date_str] = row
    except FileNotFoundError:
        pass

    # Update with ODS data
    updated_count = 0
    added_count = 0

    for _, row in df.iterrows():
        date_str = row['Week ending'].strftime('%Y-%m-%d')
        migrants = int(row['Migrants arrived']) if pd.notna(row['Migrants arrived']) else 0
        boats = int(row['Boats arrived']) if pd.notna(row['Boats arrived']) else 0

        # Handle prevention data (may be '-' or NaN)
        migrants_prevented = row.get('Migrants prevented', 0)
        events_prevented = row.get('Events prevented', 0)

        try:
            migrants_prevented = int(migrants_prevented) if pd.notna(migrants_prevented) and str(migrants_prevented) != '-' else 0
        except (ValueError, TypeError):
            migrants_prevented = 0

        try:
            events_prevented = int(events_prevented) if pd.notna(events_prevented) and str(events_prevented) != '-' else 0
        except (ValueError, TypeError):
            events_prevented = 0

        if date_str in existing_data:
            updated_count += 1
        else:
            added_count += 1

        existing_data[date_str] = [
            f'"{date_str}"',
            str(migrants),
            str(boats),
            str(migrants_prevented),
            str(events_prevented)
        ]

    # Write back sorted by date
    with open(weekly_csv, 'w') as f:
        f.write('#week_ending,migrants_arrived,boats_arrived,migrants_prevented,events_prevented\n')
        for date_str in sorted(existing_data.keys()):
            row = existing_data[date_str]
            f.write(f'{",".join(row)}\n')

    print(f'Weekly data: {updated_count} updated, {added_count} added, {len(existing_data)} total')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python backfill_from_ods.py <ods_file> <daily_csv> <weekly_csv>')
        sys.exit(1)

    ods_file = sys.argv[1]
    daily_csv = sys.argv[2]
    weekly_csv = sys.argv[3]

    print(f'Reading ODS file: {ods_file}')
    backfill_daily(ods_file, daily_csv)
    backfill_weekly(ods_file, weekly_csv)
    print('Done!')
