import shutil
import re
import json
import codecs
import os
from time import strptime
from datetime import datetime, date
from icalendar import Calendar, Event


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


with codecs.open('../README.md', 'r', encoding='utf-8-sig') as raw:
    rawLines = raw.readlines()

heading = re.compile(
    r'# Awesome Events in Italy \(([0-9]{4}) Edition\)').split(rawLines[0])
tokens = list(filter(lambda i: i != '', heading))
YEAR = int(tokens[0])


lista = list(map(lambda x: x.replace(os.linesep, ''), rawLines))

month = 0
events = []

for line in lista[lista.index('## January'):
                  len(lista) - 1 - lista[::-1].index('---')]:
    line = line + ''

    startDate = None
    endDate = None

    if line == '':
        continue

    if line.startswith('##'):
        month = strptime(line[3:], '%B').tm_mon
        continue

    chunks = re.compile(
        r'\-\ ([^]]*)\ \-\ \[([^]]*)\]\(([^\s^\)]*)[\s\)]\ \-\ ([^]]*)\ \-\ ([^]]*)\.').split(line)

    params = list(filter(lambda i: i != '', chunks))

    if len(params) != 5:
        raise SystemError(line)

    if params[0].find('-') > 0:
        days = params[0].split('-')
        startDate = date(YEAR, month, int(days[0]))

        if days[1].isdigit():
            endDate = date(YEAR, month, int(days[1]))
        else:
            endDay = days[1].split(' ')
            endMonth = month = strptime(endDay[0], '%B').tm_mon
            endYear = YEAR

            if endMonth < month:
                endYear += 1

            endDate = date(endYear, endMonth, int(endDay[1]))

    else:
        startDate = date(YEAR, month, int(params[0]))

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

dataDir = '../data/'

if (os.path.exists(dataDir)):
    shutil.rmtree(dataDir)

os.mkdir(dataDir)

# write json
with codecs.open(f'{dataDir}{YEAR}.json', 'w', encoding='utf-8-sig') as data:
    json.dump(events, data, indent=4, default=obj_dict,
              ensure_ascii=False)

# write iCal
cal = Calendar()

for awesomeEvent in events:
    event = Event()

    event.add('summary', awesomeEvent.title)
    event.add('dtstart', datetime.strptime(
        f'{awesomeEvent.startDate} 08:00', '%Y-%m-%d %H:%M'))
    event.add('dtend', datetime.strptime(
        f'{awesomeEvent.endDate} 18:00', '%Y-%m-%d %H:%M'))
    event.add('description',
              f'{awesomeEvent.description} - {awesomeEvent.url}')
    event.add('location', awesomeEvent.location)
    cal.add_component(event)

with open(f'{dataDir}{YEAR}.ics', 'wb') as ics:
    ics.write(cal.to_ical())
