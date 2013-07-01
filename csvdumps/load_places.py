import sys
from voyages.apps.voyage.models import *

# Load the source csv to the database
if len(sys.argv) > 0:
    input_file = open(sys.argv[0], 'r')
else:
    input_file = open('places.csv', 'r')

NULL_VAL = "\N"
DELIMITER = ','
first_line = input_file.readline()
data = first_line.split(DELIMITER)
varNameDict = {}

for index, term in enumerate(data):
    varNameDict[term] = index


def isNotBlank(field_name):
    return data[varNameDict[field_name]] != NULL_VAL


def getFieldValue(field_name):
    return data[varNameDict[field_name]]


def getIntFieldValue(field_name):
    try:
        if not isNotBlank(field_name):
            return None
        return int(getFieldValue(field_name))
    except ValueError:
        return None


def getDecimalFieldValue(field_name):
    try:
        if not isNotBlank(field_name):
            return None
        return float(getFieldValue(field_name))
    except ValueError:
        return None

for line in input_file:
    data = line.split(DELIMITER)

    location = Place()
    location.name = getFieldValue('name')
    location.code = getFieldValue('id')
    location.longitude = getDecimalFieldValue('longitude')
    location.latitude = getDecimalFieldValue('latitude')
    if isNotBlank('region_id'):
        location.region = Region.objects.filter(code=getIntFieldValue('region_id'))

    location.save()