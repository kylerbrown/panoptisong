"""panoptisong.py

toolset for monitoring birdsong
"""

from time import sleep
from datetime import datetime, timedelta


def sleep_daily_till(hour):
    ''' sleeps process until HOUR,
    uses 24h style, not AM/PM.

    EG sleep_daily_till(15) will return at the next 3pm.
    '''
    t = datetime.today()
    future = datetime(t.year, t.month, t.day, hour, 0)
    if t.hour >= hour:
        future += timedelta(days=1)
    sleep((future-t).seconds)
    print(datetime.today())


if __name__ == "__main__":
    pass
