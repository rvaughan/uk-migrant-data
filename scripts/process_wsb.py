"""
Simple script for processing the UK Governments weekly small boat data.
"""
from datetime import datetime
import os.path
import sys

from bs4 import BeautifulSoup
import requests


if len(sys.argv) < 4:
    print('Missing parameters')
    sys.exit(-1)

today=sys.argv[1]
input_file=sys.argv[2]
output_folder=sys.argv[3]

with open(input_file, 'r') as f:
    html = BeautifulSoup(f, features="html.parser")

    tags = html.find_all('a', attrs={'class': 'govuk-link'})
    for tag in tags:
        if 'Weekly number of migrants detected in small boats' in tag.text:
            filename = tag['href'].split('/')[-1].replace('weekly-number-of-migrants-detected-in-small-boats-', '')
            if not os.path.exists(f'{output_folder}/{filename}.html'):
                r = requests.get(f'https://www.gov.uk{tag["href"]}')
                if r.status_code == 200:
                    with open(f'{output_folder}/{filename}.html', 'w') as of:
                        of.write(r.text)

                    with open(f'{output_folder}/data.csv', 'a+') as of:
                        week_html = BeautifulSoup(r.text, features="html.parser")

                        rows = week_html.find_all('tr')

                        for row in rows[1:]:
                            dt = None
                            data = []

                            cells = row.find_all('td')
                            first = True
                            for cell in cells:
                                if first:
                                    dt = datetime.strptime(cell.text, '%d %B %Y')
                                    first = False
                                else:
                                    data.append(cell.text.split()[0].strip())

                            of.write(f'"{dt.strftime("%Y-%m-%d")}",{",".join(data)}\n')
