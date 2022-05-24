"""
Simple script for processing the UK Governments small boat data.
"""
import sys

from bs4 import BeautifulSoup


if len(sys.argv) < 4:
    print('Missing parameters')
    sys.exit(-1)

today=sys.argv[1]
input_file=sys.argv[2]
output_file=sys.argv[3]

num_migrants=0
num_boats=0

with open(input_file, 'r') as f:
    html = BeautifulSoup(f, features="html.parser")

    tags = html.find_all('h4')
    for tag in tags:
        if 'Number of migrants detected in small boats:' in tag.text:
            num_migrants = int(tag.text.split('Number of migrants detected in small boats:')[1])
        elif 'Number of boats detected:' in tag.text:
            num_boats = int(tag.text.split('Number of boats detected:')[1])

with open(output_file, 'a+') as f:
    f.write(f'"{today}",{num_migrants},{num_boats}\n')
