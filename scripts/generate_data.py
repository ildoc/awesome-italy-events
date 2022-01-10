import re
import json
import codecs
import os
from time import strptime
from datetime import date, timedelta
from icalendar import Calendar, Event
from pathlib import Path

from scripts.awesome_event import AwesomeEvent


def parse_data(path):
    with codecs.open(path, 'r', encoding='utf-8-sig') as raw:
        raw_lines = raw.readlines()

    heading = re.compile(r'# Awesome Events in Italy \(([0-9]{4}) Edition\)').split(raw_lines[0])
    tokens = list(filter(lambda i: i != '', heading))
    current_file_year = int(tokens[0])

    lista = list(map(lambda x: x.replace(os.linesep, ''), raw_lines))

    month = 0
    events_recovered = []
    debug_index = lista.index('## January') - 1

    for line in lista[lista.index('## January'): len(lista) - 1 - lista[::-1].index('---')]:
        line = line + ''
        debug_index += 1

        if line.strip() == '':
            continue

        if line.startswith('##'):
            month = strptime(line[3:], '%B').tm_mon
            continue

        try:
            awesome_event = AwesomeEvent.build_by_parsing(current_file_year, month, line)
            events_recovered.append(awesome_event.to_dict())
        except ValueError:
            print(f'Error values in line {debug_index}\n {line}')
            continue
    return events_recovered, current_file_year


def write_json(events, year, dataDir):
    # write json
    with codecs.open(f'{dataDir}{year}.json', 'w', encoding='utf-8-sig') as jsonFile:
        json.dump(events, jsonFile, indent=4, ensure_ascii=False)


def write_ical(events, year, data_dir):
    # write iCal
    cal = Calendar()

    for awesome_event in events:
        event = Event()

        event.add('summary', awesome_event['title'])
        event.add('dtstart', date.fromisoformat(awesome_event['startDate']))
        event.add('dtend', date.fromisoformat(awesome_event['endDate']) + timedelta(days=1))
        event.add('description', f"{awesome_event['description']} - {awesome_event['url']}")
        event.add('location', awesome_event['location'])
        cal.add_component(event)

    with open(f'{data_dir}{year}.ics', 'wb') as ics:
        ics.write(cal.to_ical())


files = ['../README.md', '../2022.md', '../archive/2020.md', '../archive/2019.md']
data_dir = '../data/'

if not os.path.exists(data_dir):
    os.mkdir(data_dir)

for file in files:
    try:
        events, year = parse_data(file)
        for p in Path(data_dir).glob(f'{year}.*'):
            p.unlink()
        write_json(events, year, data_dir)
        write_ical(events, year, data_dir)
    except ValueError as e:
        raise Exception(f'Parse failed {e.args} - ({file})')
