from .get_postalcodes import get_postalcodes

import osmium as osm
import pandas as pd


# https://stackoverflow.com/questions/45771809/how-to-extract-and-visualize-data-from-osm-file-in-python

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

class OSMHandler(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = {}
    def tag_inventory(self, elem, elem_type):
        id = str(elem.id)
        self.osm_data[id] = {}
        self.osm_data[id]['elem_type'] = elem_type
        for tag in elem.tags:
            self.osm_data[id][tag.k] = tag.v
        if elem_type == 'node':
            location = str(elem.location).split('/')
            self.osm_data[id]['coord'] = {}
            self.osm_data[id]['coord']['lat'] = location[1]
            self.osm_data[id]['coord']['lon'] = location[0]
        if elem_type == 'relation':
            self.osm_data[id]['members'] = {}
            for member in elem.members:
                role = ''
                mem_type = ''
                mem_split = member.split('@')
                self.osm_data[id]['members'][member.ref] = {}
                if member.startswith('w'):
                    mem_type = 'way'
                elif member.startswith('n'):
                    mem_type = 'node'
                if len(mem_split) > 1:
                    role = mem_split[-1]
                self.osm_data[id]['members'][member.ref]['type'] = mem_type
                self.osm_data[id]['members'][member.ref]['role'] = role
        if elem_type == 'way':
            self.osm_data[id]['nodes'] = []
            for node in elem.nodes:
                self.osm_data[id]['nodes'].append(str(node))
    def node(self, n):
        self.tag_inventory(n, "node")
    def way(self, w):
        self.tag_inventory(w, "way")
    def relation(self, r):
        self.tag_inventory(r, "relation")

# path to pbf file
file_path = "/Users/mariusschmiedt/Downloads/saarland-latest.osm.pbf"
# initialize OSM handler
osmhandler = OSMHandler()
# scan the input file and fills the handler list accordingly
osmhandler.apply_file(file_path)

with_zip = True

if with_zip:
    df_addresses = get_postalcodes(file_path)
else:
    relations = {}
    for key in osmhandler.osm_data.keys():
        elem = osmhandler.osm_data[key]
        if elem['elem_type'] == 'relation':
            if 'boundary' in elem:
                if elem['boundary'] == 'administrative':
                    relations[key] = {}
                    relations[key]['admin_level'] = elem['boundary']
                    relations[key]['name'] = elem['name']
                    relations[key]['place'] = elem['place']
                    for member in elem['members'].keys():
                        if elem['members'][member]['type'] == 'way' and elem['members'][member]['type'] == 'outer':
                            for node in osmhandler.osm_data[member]['nodes']:
                                relations[key][node] = osmhandler.osm_data[node]
                        else:
                            relations[key][member] = osmhandler.osm_data[member]

    for elem in osmhandler.osm_data:
        # if 'lat' in elem and 'lon' in elem  and 'addr:country' in elem and ('addr:city:en' in elem or 'addr:city' in elem) and ('addr:suburb' in elem or 'addr:suburb:en' in elem or 'addr:district:en' in elem or 'addr:district' in elem):
        if 'lat' in elem and 'lon' in elem and ('addr:city:en' in elem or 'addr:city' in elem) and ('addr:suburb' in elem or 'addr:suburb:en' in elem or 'addr:district:en' in elem or 'addr:district' in elem):
            # if elem['addr:country'] == 'AE':
            district = ''
            if 'addr:suburb:en' in elem:
                district = elem['addr:suburb:en']
            if 'addr:suburb' in elem and district == '':
                district = elem['addr:suburb']
            if 'addr:district:en' in elem and district == '':
                district = elem['addr:district:en']
            if 'addr:district' in elem and district == '':
                district = elem['addr:district']
            
            if 'addr:city:en' in elem:
                city = elem['addr:city:en']
            if 'addr:city' in elem and city == '':
                city = elem['addr:city']
            
            district = district.lower().replace(' ', '_').replace("'", "_").replace('(', '').replace(')', '')
            city = city.lower().replace(' ', '_').replace("'", "_").replace('(', '').replace(')', '')
            lat = elem['lat']
            lon = elem['lon']
            if isEnglish(city) and isEnglish(district):
                add_entry = False
                if bool(data):
                    if city in data:
                        if district in data[city]:
                            if float(lat) < float(data[city][district]['min_lat']):
                                data[city][district]['min_lat'] = lat
                            if float(lat) > float(data[city][district]['max_lat']):
                                data[city][district]['max_lat'] = lat
                            if float(lon) < float(data[city][district]['min_lon']):
                                data[city][district]['min_lon'] = lon
                            if float(lon) > float(data[city][district]['max_lon']):
                                data[city][district]['max_lon'] = lon
                        else:
                            data[city][district] = {}
                            add_entry = True
                    else:
                        data[city] = {}
                        data[city][district] = {}
                        add_entry = True
                else:
                    data[city] = {}
                    data[city][district] = {}
                    add_entry = True
                if add_entry:
                    data[city][district]['min_lat'] = lat
                    data[city][district]['max_lat'] = lat
                    data[city][district]['min_lon'] = lon
                    data[city][district]['max_lon'] = lon
