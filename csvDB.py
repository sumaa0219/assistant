import csv
from datetime import datetime


def lastTime(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        last_row = None
        for row in reader:
            last_row = row
        if last_row:
            return datetime.strptime(last_row[0], '%Y-%m-%d %H:%M:%S.%f')
        else:
            return None


def getData(filename, count):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        return rows[-count:] if count <= len(rows) else rows
