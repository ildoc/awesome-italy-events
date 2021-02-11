import shutil
import re
import json
import codecs
import os
from time import strptime
from datetime import date, timedelta
from icalendar import Calendar, Event
from pathlib import Path


class AwesomeEvent:
    def __init__(
        self,
        title,
        url,
        description,
        location,
        startDate,
        endDate=None
    ):
        self.title = title
        self.url = url
        self.description = description
        self.location = location
        self.startDate = str(startDate)
        self.endDate = str(endDate or startDate)


def obj_dict(obj):
    return obj.__dict__


def parse_data(path):
    with codecs.open(path, 'r', encoding='utf-8-sig') as raw:
        rawLines = raw.readlines()

    heading = re.compile(
        r'# Awesome Events in Italy \(([0-9]{4}) Edition\)').split(rawLines[0])
    tokens = list(filter(lambda i: i != '', heading))
    year = int(tokens[0])

    lista = list(map(lambda x: x.replace(os.linesep, ''), rawLines))

    month = 0
    events = []
    debugIndex = lista.index('## January') - 1

    for line in lista[lista.index('## January'):
                      len(lista) - 1 - lista[::-1].index('---')]:
        line = line + ''
        debugIndex += 1

        startDate = None
        endDate = None

        if line.strip() == '':
            continue

        if line.startswith('##'):
            month = strptime(line[3:], '%B').tm_mon
            continue

        chunks = re.compile(
            r'\-\ ([^]]*)\ \-\ \[([^]]*)\]\(([^\s^\)]*)[\s\)]\ \-\ ([^]]*)\ \-\ ([^]]*)\.').split(line)

        params = list(filter(lambda i: i != '', chunks))

        if len(params) != 5:
            raise ValueError(f'line {debugIndex}: {line}')

        if params[0].find('-') > 0:
            days = params[0].split('-')
            startDate = date(year, month, int(days[0]))

            if days[1].isdigit():
                endDate = date(year, month, int(days[1]))
            else:
                endDay = days[1].split(' ')
                endMonth = month = strptime(endDay[0], '%B').tm_mon
                endYear = year

                if endMonth < month:
                    endYear += 1

                endDate = date(endYear, endMonth, int(endDay[1]))

        else:
            startDate = date(year, month, int(params[0]))

        events.append(
            AwesomeEvent(
                title=params[1],
                url=params[2],
                location=params[3],
                description=params[4],
                startDate=startDate,
                endDate=endDate
            )
        )
    return (events, year)


def write_json(events, year, dataDir):
    # write json
    with codecs.open(f'{dataDir}{year}.json', 'w', encoding='utf-8-sig') as jsonFile:
        json.dump(events, jsonFile, indent=4, default=obj_dict,
                  ensure_ascii=False)


def write_ical(events, year, dataDir):
    # write iCal
    cal = Calendar()

    for awesomeEvent in events:
        event = Event()

        event.add('summary', awesomeEvent.title)
        event.add('dtstart', date.fromisoformat(awesomeEvent.startDate))
        event.add('dtend', date.fromisoformat(
            awesomeEvent.endDate) + timedelta(days=1))
        event.add('description',
                  f'{awesomeEvent.description} - {awesomeEvent.url}')
        event.add('location', awesomeEvent.location)
        cal.add_component(event)

    with open(f'{dataDir}{year}.ics', 'wb') as ics:
        ics.write(cal.to_ical())


files = ['../README.md', '../2022.md', '../archive/2020.md', '../archive/2019.md']
dataDir = '../data/'

if not os.path.exists(dataDir):
    os.mkdir(dataDir)

for file in files:
    try:
        (events, year) = parse_data(file)
        for p in Path(dataDir).glob(f'{year}.*'):
            p.unlink()
        write_json(events, year, dataDir)
        write_ical(events, year, dataDir)
    except ValueError as e:
        raise Exception(f'Parse failed {e.args} - ({file})')
