from voyages.apps.voyage.models import *

# Load the source csv to the database

input_file = open('csvdumps/broadregion.csv', 'r')

NULL_VAL = "\N"
DELIMITER = ','

first_line = input_file.readline()

data = first_line[0:-2].split(DELIMITER)
print len(data)

varNameDict = {}
for index, term in enumerate(data):
    varNameDict[term[1:-1]] = index


def isNotBlank(field_name):
    return data[varNameDict[field_name]][1:-1] != NULL_VAL


def getFieldValue(field_name):
    print field_name
    return data[varNameDict[field_name]][1:-1]


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
    # Ignore the \r and \n character
    data = line[0:-2].split(DELIMITER)

    print data

    b_region = BroadRegion()
    b_region.name = getFieldValue('name')

    b_region.code = getIntFieldValue('id')
    if getFieldValue('show_on_map') == "t":
        b_region.show_on_map = True
    else:
        b_region.show_on_map = False

    b_region.save()