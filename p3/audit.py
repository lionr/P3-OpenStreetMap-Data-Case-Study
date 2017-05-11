import xml.etree.cElementTree as ET
import re
from collections import defaultdict
import pprint
import cerberus
import schema1
import csv
import codecs
OSMFILE = 'Austin.osm'
osm_file = open(OSMFILE, "r")

# find unexpected street types
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected = ["Street", "Avenue", "Boulevard", "Road", "Drive", "Lane", "Circle", "Highway", "Terrace",\
            "Walk", "Place", "Court", "Cove", "Crescent", "Parkway", "Trail", "Square"]

mapping = { "St.": "Street",
            "St": "Street",
            "Rd": "Road",
            "Ave": "Avenue",
            "Speedway": "Highway",
            "Lanes": "Lane",
            "Blvd": "Boulevard",
            "E": "East",
            "W": "West",
            "N": "North",
            "S": "South",
            "E.": "East",
            "W.": "West",
            "N.": "North",
            "S.": "South"
           }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v)

def audit():
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

if __name__ == '__main__':
    pprint.pprint(dict(audit())) 
        
# fix the unexpected street types to the appropriate ones
def update_street_name(name, mapping):
    name_split = name.split()
    begin = name_split[0]
    last = name_split[-1]
    if begin in mapping:
        name_split[0] = mapping[begin]
    if last in mapping:
        name_split[-1] = mapping[last]
        delimiter = ' '
        return delimiter.join(name_split)
    else:
        return name
    
st_types = audit()

for st_type, ways in st_types.iteritems():
    for name in ways:
        print name, "=>", update_street_name(name, mapping)

# correct phone number format
PHONENUM = re.compile(r'\+1\s\d{3}\s\d{3}\s\d{4}')    

def update_phone_num(phone_num):
    # Check for valid phone number format
    m = PHONENUM.match(phone_num)
    if m is None:
        # Convert all dashes to spaces
        if "-" in phone_num:
            phone_num = re.sub("-", " ", phone_num)
        # Remove all brackets
        if "(" in phone_num or ")" in phone_num:
            phone_num = re.sub("[()]", "", phone_num)
        # Space out 10 straight numbers
        if re.match(r'\d{10}', phone_num) is not None:
            phone_num = phone_num[:3] + " " + phone_num[3:6] + " " + phone_num[6:]
        # Space out 11 straight numbers
        elif re.match(r'\d{11}', phone_num) is not None:
            phone_num = phone_num[:1] + " " + phone_num[1:4] + " " + phone_num[4:7] + " " + phone_num[7:]
        # Add full country code
        if re.match(r'\d{3}\s\d{3}\s\d{4}', phone_num) is not None:
            phone_num = "+1 " + phone_num
        # Add + in country code
        elif re.match(r'1\s\d{3}\s\d{3}\s\d{4}', phone_num) is not None:
            phone_num = "+" + phone_num
        # Ignore tag if no area code and local number (<10 digits)
        elif sum(c.isdigit() for c in phone_num) < 10:
            return None
    return phone_num

osm_file.seek(0)
for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "phone":
                    print tag.attrib['v'], "=>", update_phone_num(tag.attrib['v'])
