"""panoptisong.py

toolset for monitoring birdsong
"""

from subprocess import Popen
from time import sleep
from datetime import datetime, timedelta
import json


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


def load_config_file(json_file):
    """loads a config file in json format"""
    with open(json_file, 'r') as f:
        conf = json.load(f)
    return (conf["birds"], conf["boxes"],
            conf["global-attributes"])


def start_jdetect(boxes):
    for box in boxes:
        detect_params = box["jdetect"]
        Popen(['jdetect',
               '-C', detect_params])


if __name__ == "__main__":
    birds, boxes, attrs = load_config_file("example.json")
