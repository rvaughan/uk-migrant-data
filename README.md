# UK Government Immigration and Migrant Data

[![Fetch daily UK small boat data](https://github.com/rvaughan/uk-migrant-data/actions/workflows/daily_small_boats.yml/badge.svg)](https://github.com/rvaughan/uk-migrant-data/actions/workflows/daily_small_boats.yml)
[![Process daily small boats data](https://github.com/rvaughan/uk-migrant-data/actions/workflows/process_dsb.yml/badge.svg)](https://github.com/rvaughan/uk-migrant-data/actions/workflows/process_dsb.yml)
[![Fetch weekly UK small boat data](https://github.com/rvaughan/uk-migrant-data/actions/workflows/weekly_small_boats.yml/badge.svg)](https://github.com/rvaughan/uk-migrant-data/actions/workflows/weekly_small_boats.yml)
[![Process weekly small boats data](https://github.com/rvaughan/uk-migrant-data/actions/workflows/process_wsb.yml/badge.svg)](https://github.com/rvaughan/uk-migrant-data/actions/workflows/process_wsb.yml)

This project tracks UK Government immigration and migrant data sets, providing a simple overview
of the results that is hopefully easy to understand.

## Datasets Used

### Small Boat Crossing Data

The UK Government changed the location of small boat crossing data in early 2023. The old data sources are now legacy pages that are no longer updated.

**Current data sources:**
  * [Daily small boat crossing data (last 7 days)](https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats/migrants-detected-crossing-the-english-channel-in-small-boats-last-7-days) - Updated daily
  * [Weekly small boat summary](https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats/weekly-summary-of-small-boat-arrivals-and-preventions) - Updated weekly on Fridays
  * [Time series (ODS)](https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats) - Complete historical data from 2018, updated weekly on Fridays

**Legacy data sources (no longer updated):**
  * ~~[Daily small boat crossing data](https://www.gov.uk/government/statistical-data-sets/migrants-detected-crossing-the-english-channel-in-small-boats)~~
  * ~~[Weekly small boat crossing data](https://www.gov.uk/government/statistics/migrants-detected-crossing-the-english-channel-in-small-boats-weekly-data)~~

### Other Datasets

  * [ONS: Economic Activity (INAC01 SA)](https://www.ons.gov.uk/employmentandlabourmarket/peoplenotinwork/economicinactivity/datasets/economicinactivitybyreasonseasonallyadjustedinac01sa)
  * [ONS: Employment by country of birth and nationality (EMP06)](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/employmentbycountryofbirthandnationalityemp06)
  * [ONS: Labour Market (AP2Y)](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/timeseries/ap2y/unem)
  * [ONS: Labour Market (MGWG)](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/timeseries/mgwg/lms)
  * [ONS: Population Statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/timeseries/ukpop/pop)
      * [ONS: Annual Midyear Statistics (mid2020)](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/bulletins/annualmidyearpopulationestimates/mid2020)

## Data Formats

### Daily Small Boats (`data/daily_small_boats/data.csv`)

```csv
#date,migrants,boats
"2025-12-13",737,11
```

Contains daily counts of migrants and boats detected crossing the English Channel.

### Weekly Small Boats (`data/weekly_small_boats/data.csv`)

```csv
#week_ending,migrants_arrived,boats_arrived,migrants_prevented,events_prevented
"2025-12-07",0,0,438,11
```

Contains weekly aggregate data including prevention statistics (available from 2024 onwards).

## Backfilling Missing Data

If data is missing or needs to be refreshed from the official time series, you can use the backfill script with the ODS file from GOV.UK:

1. Download the latest time series ODS file from [GOV.UK](https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats)

2. Install dependencies:
   ```bash
   pip install pandas odfpy beautifulsoup4
   ```

3. Run the backfill script:
   ```bash
   python scripts/backfill_from_ods.py <path_to_ods_file> data/daily_small_boats/data.csv data/weekly_small_boats/data.csv
   ```

This will update both daily and weekly CSV files with complete historical data from the ODS file.
