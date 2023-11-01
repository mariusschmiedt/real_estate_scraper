from ..utils import getDataBaseConfig

class writeListing():
    def __init__(self, sql, update_prices = False):
        
        self.sql = sql
        self.finish = False
        self.update_prices = update_prices

    def writeListingToDb(self, listing):
        
        # query to check if an entry is already in the database
        self.sql.cur.execute("SELECT id FROM " + self.sql.table_name + " WHERE provider_id = '" + listing["provider_id"] + "' AND provider = '" + listing["provider"]  + "'")
        existingID = self.sql.cur.fetchall()
        
        # query to check if a similar entry is already in the database
        fieldsToCheck = ["price", "size", "rooms", "address_id"]
        select_str = ' AND '.join([fieldsToCheck[idx] + " = '" + listing[fieldsToCheck[idx]] + "'" for idx in range(len(fieldsToCheck))])
        self.sql.cur.execute("SELECT id FROM " + self.sql.table_name + " WHERE " + select_str)
        similarId = self.sql.cur.fetchall()

        if len(existingID) != 0 and not self.update_prices:
            self.finish = True

        # if an address has been found and also the price and size is valied
        if listing['address_id'] != '' and listing['price_per_space'] != '':
            # if the entry does not exist
            if len(existingID) == 0 and len(similarId) == 0:
                self.sql.cur.execute("INSERT INTO " + self.sql.table_name + " (provider, url, provider_id, title, address_id, address_detected, price, currency, size, size_unit, rooms, price_per_space, type, in_db_since, active) VALUES ('" + listing['provider'] + "','" + listing['url'] + "','" + listing['provider_id'] + "','" + listing['title'] + "'," + listing['address_id'] + ",'" +  listing['address_detected'] + "','" + listing['price'] + "','" + listing['currency'] + "','" + listing['size'] + "','" + listing['size_unit'] + "','" + listing['rooms'] +  "','" + listing['price_per_space'] + "','" + listing['type'] + "','" + listing['in_db_since'] + "'," + listing['active'] + ")")
            else:
                # if the entry does exist check for price changes
                if len(existingID) != 0 and not self.finish:
                    # id of the existing entry
                    dbId = str(existingID[0][0])
                    # select significant values to detect changes
                    self.sql.cur.execute("SELECT price FROM " + self.sql.table_name + " WHERE id = " + dbId + "")
                    price_in_db = self.sql.cur.fetchone()
                    price_in_listing = listing['price']
                    if float(price_in_db[0]) != float(price_in_listing):
                        self.sql.cur.execute("UPDATE " + self.sql.table_name + " SET price = '" + listing["price"] + "' WHERE ID = " + dbId + '')