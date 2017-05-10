# find unexpected street types
osm_file = open(OSMFILE, "r")

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
