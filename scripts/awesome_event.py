import re
from urllib.parse import urlparse
from datetime import date
from time import strptime


class AwesomeEvent:
    def __init__(self, title: str, url: str, description: str, location: str, start_date: date, end_date: date):
        """
        This is the AwesomeEvent object
            :param title: title of the event
            :param url: url of the event, needs to have the scheme and the net location of the url
            :param description: a brief description of the event
            :param location: the location of the event
            :param start_date: date when the event is going to start
            :param end_date: date when the event is going to end
        """
        self.title = title
        self.url = url
        self.description = description
        self.location = location
        self.start_date = start_date
        self.end_date = end_date if end_date else start_date

    def to_dict(self) -> dict:
        """
        this is the method for converting the object into a dict
        >>> AwesomeEvent('An awesome event', 'https://www.dummy.it/', 'An awesome event description', 'Milano', date(2022,2,14), date(2022,3,16)).to_dict()
        {'title': 'An awesome event', 'url': 'https://www.dummy.it/', 'description': 'An awesome event description', 'location': 'Milano', 'startDate': '2022-02-14', 'endDate': '2022-03-16'}
        """
        return {
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'location': self.location,
            'startDate': str(self.start_date),
            'endDate': str(self.end_date)
        }

    @staticmethod
    def build_by_parsing(start_year: int, start_month: int, md_row: str):
        """
        This method is responsible for the parsing of the string passed
        It needs the year as start_year as a number, the start_month as a month and the markdown string md_row
        composed as the following format:
            - {start_day(-end_day)} - [{title}]({url}) - {localtion} - {description}.
        Note : (-end_day) it's optional if the event it's just for a day
        Note2: (-end_month end_day) end_month must be the name of the month in `strptime(str(end_month), '%B').tm_mon`

        >>> awevent = AwesomeEvent.build_by_parsing(2022, 2,'- 14 - [An awesome event - 2019 edition](https://www.dummy.it/) - Milano - An awesome event description.')
        >>> awevent.title
        'An awesome event - 2019 edition'
        >>> awevent.url
        'https://www.dummy.it/'
        >>> awevent.description
        'An awesome event description'
        >>> awevent.location
        'Milano'
        >>> str(awevent.start_date)
        '2022-02-14'
        >>> str(awevent.end_date)
        '2022-02-14'
        >>> awevent = AwesomeEvent.build_by_parsing(2022, 2, '- 14-16 - [An awesome event](https://www.dummy.it/) - Milano - An awesome event.')
        >>> str(awevent.end_date)
        '2022-02-16'
        >>> awevent = AwesomeEvent.build_by_parsing(2022, 2, '- 14-June 16 - [An awesome event](https://www.dummy.it/) - Milano - An awesome event.')
        >>> str(awevent.end_date)
        '2022-06-16'
        >>> awevent = AwesomeEvent.build_by_parsing(2022, 12, '- 14-January 3 - [An awesome event](https://www.dummy.it/) - Milano - An awesome event.')
        >>> str(awevent.end_date)
        '2023-01-03'

        It's new year's eve PROOF
        """
        pattern = re.compile(r'\-\s(\d+\-?\w*\s?\d*)\s\-\s(\[([^]]*)\]\(([^)]*)\)|([^]]*))\s\-\s([^-]*)\s\-\s([^]]*)\.')
        split_str = pattern.split(md_row)[1:-1]

        if len(split_str) == 7:
            end_month = None
            is_same_day = False

            end_date = None

            if '-' in split_str[0]:
                start_day = int(split_str[0].split('-')[0])
                end_day = split_str[0].split('-')[1]

                # Validate Days value
                if start_day not in list(range(1, 32)):
                    raise ValueError(f'{start_day} and {end_day} aren\t valid days of the month')

                if end_day.isdigit():
                    end_day = int(end_day)
                    if end_day not in list(range(1, 32)):
                        raise ValueError(f'end_day {end_day} isn\'t a valid day for a month')
                else:
                    end_month, end_day = end_day.split(' ')
                    if int(end_day) not in list(range(1, 32)):
                        raise ValueError(f'end_day {end_day} isn\'t a valid day for a month')
                    end_day = int(end_day)
                    end_month = end_month
            else:
                that_day = int(split_str[0])

                # Validate Day value
                if that_day not in range(1, 32):
                    raise ValueError(f'{that_day} isn\'t a valid day for a month')
                start_day = that_day
                end_day = that_day
                is_same_day = True

            if is_same_day:
                start_date = date(start_year, start_month, start_day)
                end_date = start_date
            else:
                start_date = date(start_year, start_month, start_day)

                if end_month:
                    end_month = strptime(str(end_month), '%B').tm_mon
                    end_year = start_year

                    if end_month < start_month:
                        end_year += 1

                    end_date = date(end_year, end_month, end_day)
                else:
                    end_date = date(start_year, start_month, end_day)

            title = None
            url = None

            if split_str[4]:
                title = split_str[4]
            else:
                title, url = split_str[2], split_str[3]

            # Validate url value
            if url:
                parsed_url = urlparse(url)
                if not(len(parsed_url.scheme) > 0 and len(parsed_url.netloc) > 0):
                    raise ValueError(f'{url} isn\'t a valid url')

            location = split_str[5]
            description = split_str[6]
            return AwesomeEvent(title, url, description, location, start_date, end_date)
        else:
            print(f'Invalid row {md_row}')  # Ignoring
            return None


if __name__ == '__name__':
    import doctest
    doctest.testmod()
