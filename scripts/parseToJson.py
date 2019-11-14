import shutil
import re
import json
import codecs
import os
from time import strptime
from datetime import date


class Event:
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

print(rawLines)

heading = re.compile(
    r'# Awesome Events in Italy \(([0-9]{4}) Edition\)').split(rawLines[0])
tokens = list(filter(lambda i: i != '', heading))
YEAR = int(tokens[0])


lista = list(map(lambda x: x.replace('\r\n', ''), rawLines))

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
        Event(
            title=params[2],
            url=params[1],
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

with codecs.open(f'{dataDir}{YEAR}.json', 'w', encoding='utf-8-sig') as data:
    json.dump(events, data, indent=4, default=obj_dict,
              ensure_ascii=False)
