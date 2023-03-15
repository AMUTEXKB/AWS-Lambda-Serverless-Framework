import datetime


def convert_datetime_to_epoch(date_time):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((date_time - epoch).total_seconds() * 1000.0)


def convert_epoc_to_datetime(epoch):
    return datetime.datetime.fromtimestamp(epoch / 1000)


def convert_string_to_bool(string):
    if string.lower() == "true":
        return True
    return False
