import xml.etree.cElementTree as ET
from collections import defaultdict
import re

OSMFILE = '/Users/Liu/Self-learning/DataAnalytics/project3/austin.osm'
osm_file = open(OSMFILE, "r")

# find unexpected street types
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
PHONENUM = re.compile(r'\+1\s\d{3}\s\d{3}\s\d{4}')  
POSTCODE = re.compile(r'\b\d{5}\b')  
expected = ["Street", "Avenue", "Boulevard", "Road", "Drive", "Lane", "Circle", "Highway", "Terrace", "Park",\
            "Walk", "Place", "Court", "Cove", "Crescent", "Parkway", "Trail", "Square", "Plaza", "Path", "Way", \
            "Center", "Mission"]

mapping = { "St": "Street",
            "St.": "Street",
            "Rd":"Road",
            "Rd.": "Road",
            "Dr": "Drive",
            "Dr.": "Drive",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Speedway": "Highway",
            "Lanes": "Lane",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Ct": "Court",
            "Ct.": "Court",
            "Crt": "Court",
            "Crt.": "Court",
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
            
# fix the unexpected street types to the appropriate ones   
def update_street_name(name):
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
        delimiter = ' '
        return delimiter.join(name_split)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
           
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

# display the process of updating street names using "=>"
st_types = audit(OSMFILE)
for st_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_street_name(name)
        print name, "=>", better_name
            
# correct phone number format
def check_phone_num(phone_num):
    m = PHONENUM.match(phone_num)
    if m is None:
        return True
    
def update_phone_num(phone_num):
    # Check for valid phone number format
    m = PHONENUM.match(phone_num)
    if m is None:
        # Convert all dashes or dots to spaces
        if "-" in phone_num or "." in phone_num:
            phone_num = re.sub("[-.]", " ", phone_num)
        # Remove all brackets
        if "(" in phone_num or ")" in phone_num:
            phone_num = re.sub("[()]", "", phone_num)
        # Space out 10 straight numbers
        if re.match(r'\d{10}', phone_num) is not None:
            phone_num = phone_num[:3] + " " + phone_num[3:6] + " " + phone_num[6:]
        # Space out 11 straight numbers
        elif re.match(r'\d{11}|\+1\d{11}', phone_num) is not None:
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
# display the process of updating phone numbers with incorrect format
for event, elem in ET.iterparse(osm_file, events=("start",)): 
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "phone" and check_phone_num(tag.attrib['v']):
                print tag.attrib['v'], "=>", update_phone_num(tag.attrib['v'])

# check post code fromat
def check_post_code(post_code):
    m = POSTCODE.match(post_code)
    if m is None:
        return True
    
osm_file.seek(0)
def check_all_post_code():
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:postcode" and check_post_code(tag.attrib['v']):
                    return tag.attrib['v']
if check_all_post_code() is None:
    print "All postcodes are in the right format!"
    # after running the code, we can find that all postcodes are in the right format 
else: 
    print "Some postcodes are in the wrong format!"