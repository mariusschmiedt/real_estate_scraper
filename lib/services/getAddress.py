import geopy.geocoders
from geopy.geocoders import Nominatim
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

    if 'city' in listing:
        city = listing['city']
    if 'district' in listing:
        district = listing['district']
    if 'postalcode' in listing:
        postalcode = listing['postalcode']
    
    # if a postcode have been found define new address string e.g. 70597, Germany
    if postalcode != '' and city == '':
        address = postalcode + ', ' + country
    if postalcode == '' and city != '':
        address = city + ', ' + country
    if postalcode != '' and city != '':
        address = postalcode + ' ' + city + ', ' + country
    # if the country was not in the found address string add it to the existing one e.g. 70597 Stuttgart, Germany
    if country.lower() not in address.lower():
        address = address + ', ' + country

    # initialize the address id of the address_table
    address_id = ''

    # find address in existing database with country and postcode
    if postalcode != '' and country != '':
        found_states = sql.querySql("SELECT id, state, city, district FROM address_table WHERE postalcode='" + postalcode + "' AND country='" + country + "'")
        if len(found_states) > 0:
            found_state = found_states[0]
            address_id = str(found_state[0])
            state = found_state[1].strip()
            city = found_state[2].strip()
            district = found_state[3].strip()

    # if the address has not been found but the city and district is expected to be known from the address string
    if address_id == '' and city != '' and country != '':
        found_states = []
        if district != '':
            found_states = sql.querySql("SELECT id, state, postalcode FROM address_table WHERE city='" + city + "' AND country='" + country + "' AND district='" + district + "'")
        else:
            found_states = sql.querySql("SELECT id, state, postalcode FROM address_table WHERE city='" + city + "' AND country='" + country + "'")
        if len(found_states) == 1:
            found_state = found_states[0]
            address_id = str(found_state[0])
            state = found_state[1].strip()
            postalcode = found_state[2].strip()
    
    # if the address of the address string have not been stored in the database or could not been found use geopy
    if state == '' or city == '' or postalcode == '':
        # initialize address parts again
        country = ''
        postalcode = ''
        state = ''
        city = ''
        district = ''
        
        # define ssl certificate
        ctx = ssl.create_default_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        
        # define user ugent for Nominatim
        user_agent = 'user_me_{}'.format(randint(10000,99999))
        geolocator = Nominatim(user_agent=user_agent)
        
        # get location
        location = None
        try:
            location = geolocator.geocode(address, addressdetails=True, language='en')
        except:
            pass
        
        # try to find all address parts from postalcode and country and / or city
        country, postalcode, state, city, district = getLocationInfromation(location)

        # if not all parts could have been found get location reverse from lat and lon
        if (country == '' or postalcode == '' or state == '' or city == '') and location is not None:
            # get reverse location from lat and lon
            reverse_location = None
            try:
                reverse_location = geolocator.reverse((location.raw['lat'], location.raw['lon']), addressdetails=True, timeout=None, language='en')
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
        
        # update database if something is new
        if country != '' and postalcode != '' and state != '' and city != '':
            # check if with the new information an address id can be found
            found_states = sql.querySql("SELECT id FROM address_table WHERE postalcode='" + postalcode + "' AND country='" + country + "'")
            if len(found_states) > 0:
                found_state = found_states[0]
                address_id = str(found_state[0])
            
            # if the address is still not found add it to the database otherwise update it
            if address_id == '':
                sql.querySql("INSERT INTO address_table (country, postalcode, state, city, district) VALUES ('" + country + "','" + postalcode + "','" + state + "','" + city + "','" + district + "'); ")
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