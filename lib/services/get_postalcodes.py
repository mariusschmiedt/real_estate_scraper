import osmium as osm
import pandas as pd

# https://stackoverflow.com/questions/45771809/how-to-extract-and-visualize-data-from-osm-file-in-python

class OSMHandler(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []

    def node(self, n):
        addr_tags = [tag.k for tag in n.tags if tag.k.startswith('addr')]
        if len(addr_tags) > 0:
            addr_dict = {}
            for tag in addr_tags:
                addr_dict[tag] = n.tags[tag]
            self.osm_data.append(addr_dict)

def get_postalcodes(file_path):
    # initialize OSM handler
    osmhandler = OSMHandler()
    # scan the input file and fills the handler list accordingly
    osmhandler.apply_file(file_path)

    file_path = "/Users/mariusschmiedt/Downloads/gcc-states-latest.osm.pbf"
    # initialize OSM handler
    osmhandler = OSMHandler()
    # scan the input file and fills the handler list accordingly
    osmhandler.apply_file(file_path)
    postalcodes = list()
    data = list()    
    for elem in osmhandler.osm_data:
        if 'addr:postcode' in elem and 'addr:country' in elem and 'addr:city' in elem and 'addr:suburb' in elem and not elem['addr:postcode'] in postalcodes:
            data.append(elem)
            postalcodes.append(elem['addr:postcode'])
    for elem in osmhandler.osm_data:
        if 'addr:postcode' in elem and 'addr:country' in elem and 'addr:city' in elem and not elem['addr:postcode'] in postalcodes:
            data.append(elem)
            postalcodes.append(elem['addr:postcode'])
    addresses = list()
    for d in data:
        if d['addr:country'] == 'DE':
            postalcode = d['addr:postcode']
            city = d['addr:city']
            district = ''
            if 'addr:suburb' in d:
                district = d['addr:suburb']
            addresses.append([postalcode, city, district])

    return pd.DataFrame(addresses, columns=['postalcode', 'city', 'district'])