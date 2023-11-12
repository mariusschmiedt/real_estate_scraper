import geopy.geocoders
from geopy.geocoders import Nominatim
import math
import certifi
import ssl
from random import randint

def getAddress(listing, country, sql):
    # get address string of offer
    address = listing['address_detected']

    # initialize address parts
    postalcode = ''
    state = ''
    city = ''
    district = ''
    lat = ''
    lon = ''

    # if address contains lat and lon info extract them (in UAE not postalcode are existing)
    if 'lat:' in address and 'lon:' in address:
        add_split = address.split(',')
        for a in add_split:
            if 'lat:' in a:
                lat = a.replace('lat:', '').strip()
            if 'lon:' in a:
                lon = a.replace('lon:', '').strip()
    
    coord_from_address = False
    if lat != '' and lon != '':
        coord_from_address = True

    # if a postcode or city have been found define new address string e.g. 70176, Germany or Stuttgart, Germany
    if 'postalcode' in listing:
        address = listing['postalcode'] + ', ' + country
    if 'city' in listing and not 'postalcode' in listing:
        address = listing['city'] + ', ' + country
    # if the postalcode or city could not be extracted and the country is not part of the address add the country
    if country.lower() not in address.lower() and lat == '' and lon == '':
        address = address + ', ' + country

    # initialize the address id of the address_table
    address_id = ''

    # find address in existing database with country and postalcode if available
    if 'postalcode' in listing and country != '':
        found_states = sql.querySql("SELECT id FROM address_table WHERE postalcode='" + listing['postalcode'] + "' AND country='" + country + "'")
        if len(found_states) > 0:
            address_id = str(found_states[0][0])
    
    # if lat and lon is available find nearby (750 m) addresses
    if lat != '' and lon != '':
        found_coords = sql.querySql("SELECT id FROM address_table WHERE lat =" + lat + " AND lon =" + lon + "")
        if len(found_coords) > 0:
            address_id = str(found_coords[0][0])
        else:
            # convert to number
            lat_num = float(lat)
            lon_num = float(lon)
            # set distance to build a square
            dist = 0.75
            # scope of the earth
            scope_earth = 40075
            # get latitude deviation for the desired distance
            lat_deviation = round((360 / scope_earth) * dist , 7)
            # get longitudinal deviation for the desired distance based on the latitude value
            lon_deviation = round((360/(math.cos(lat_num * math.pi / 180) * scope_earth)) * dist , 7)

            # define upper and lower bounds
            upper_lat = str(lat_num + lat_deviation)
            lower_lat = str(lat_num - lat_deviation)
            upper_lon = str(lon_num + lon_deviation)
            lower_lon = str(lon_num - lon_deviation)
            # find address within the bounds
            found_coords = sql.querySql("SELECT id, lat, lon FROM address_table WHERE lat >" + lower_lat + " AND lat <" + upper_lat + " AND lon >" + lower_lon + " AND lon <" + upper_lon + "")
            # if addresses have been found check for the closest found address and assign the same id
            if len(found_coords) > 0:
                dist = 10
                for coord in found_coords:
                    comp_lat = coord[1]
                    comp_lon = coord[2]
                    dist_temp = math.sqrt(math.pow(lat_num - comp_lat, 2) + math.pow(lon_num - comp_lon, 2))
                    if dist_temp < dist:
                        dist = dist_temp
                        address_id = str(coord[0])
                if address_id == '':
                    address_id = str(found_coords[0][0])

    # if not any similar address could be found use geopy
    if address_id == '':

        # define ssl certificate
        ctx = ssl.create_default_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        
        # define user ugent for Nominatim
        user_agent = 'user_me_{}'.format(randint(10000,99999))
        geolocator = Nominatim(user_agent=user_agent)
        
        # get location from address if lat and lon is not defined
        location = None
        if lat == '' and lon == '':
            try:
                location = geolocator.geocode(address, addressdetails=True, language='en')
            except:
                pass
        
        # try to find all address parts from postalcode and country and / or city
        country, postalcode, state, city, district = getLocationInfromation(location)
        
        # get lat lon from found location
        if location is not None:
            lat = location.raw['lat']
            lon = location.raw['lon']
        
        # if not all parts could have been found get location reverse from lat and lon
        if (country == '' or postalcode == '' or state == '' or city == '') and lat != '' and lon != '':
            # get reverse location from lat and lon
            reverse_location = None
            
            try:
                reverse_location = geolocator.reverse((lat, lon), addressdetails=True, timeout=None, language='en')
            except:
                pass
            
            # get address parts from reverse location
            rev_country, rev_postalcode, rev_state, rev_city, rev_district = getLocationInfromation(reverse_location)
            
            # only update parts if it not already has been found
            if country == '' and rev_country != '':
                country = rev_country
            if postalcode == '' and rev_postalcode != '':
                postalcode = rev_postalcode
            if state == '' and rev_state != '':
                state = rev_state
            if city == '' and rev_city != '':
                city = rev_city
            if district == '' and rev_district != '':
                district = rev_district
            if country == 'United Arab Emirates':
                if city == '' and state != '':
                    city = state.replace('Emirate', '').strip()
        country = country.replace("'", "''")
        state = state.replace("'", "''")
        city = city.replace("'", "''")
        district = district.replace("'", "''")
        # update database if something is new
        if country != '' and state != '' and city != '' and (postalcode != '' or coord_from_address):
            # check if with the new information an address id can be found
            found_states = sql.querySql("SELECT id FROM address_table WHERE country='" + country + "' AND postalcode='" + postalcode + "' AND state='" + state + "' AND city='" + city +"'")
            if len(found_states) > 0:
                found_state = found_states[0]
                address_id = str(found_state[0])
            
            # if the address is still not found add it to the database otherwise update it
            if address_id == '':
                sql.querySql("INSERT INTO address_table (country, postalcode, state, city, district, lat, lon) VALUES ('" + country + "','" + postalcode + "','" + state + "','" + city + "','" + district + "'," + lat + "," + lon + "); ")
                # get the id after it has been added
                found_states = sql.querySql("SELECT id FROM address_table WHERE country='" + country + "' AND postalcode='" + postalcode + "' AND state='" + state + "' AND city='" + city + "' AND district='" + district +"'")
                if len(found_states) > 0:
                    found_state = found_states[0]
                    address_id = str(found_state[0])

                # if the id is still not available leave the district open
                if address_id == '':
                    found_states = sql.querySql("SELECT id FROM address_table WHERE country='" + country + "' AND postalcode='" + postalcode + "' AND state='" + state + "' AND city='" + city +"'")
                    if len(found_states) > 0:
                        found_state = found_states[0]
                        address_id = str(found_state[0])
            else:
                sql.querySql("UPDATE address_table SET country = '" + country + "', postalcode='" + postalcode + "', state='" + state + "', city='" + city + "', district='" + district + "' WHERE id = " + str(address_id) + '')

    # assign the address if to the listing
    listing['address_id'] = address_id
    return listing

def getLocationInfromation(location):
    # get the location parts from geopy
    country = ''
    postalcode = ''
    state = ''
    city = ''
    district = ''
    if location is not None:
        if 'address' in location.raw:
            if 'postcode' in location.raw['address']:
                postalcode = location.raw['address']['postcode']
            if 'city' in location.raw['address']:
                city = location.raw['address']['city']
            if 'town' in location.raw['address'] and city == '':
                city = location.raw['address']['town']
            if 'village' in location.raw['address'] and city == '':
                city = location.raw['address']['village']
            if 'state' in location.raw['address']:
                state = location.raw['address']['state']
            if city != '' and state == '':
                state = city
            if 'suburb' in location.raw['address']:
                district = location.raw['address']['suburb']
            if 'country' in location.raw['address']:
                country = location.raw['address']['country']
    
    return country, postalcode, state, city, district