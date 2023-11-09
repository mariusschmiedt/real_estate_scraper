import mysql.connector
import datetime
import pandas as pd
import requests
from ..utils import getDataBaseConfig

class sqlConnection():
    def __init__(self, table_name, base_path, table_columns=None):
        self.config = getDataBaseConfig(base_path)
        self.mydb = None
        self.cur = None
        
        self.table_name = table_name
        self.table_columns = table_columns
        
    def openMySQL(self):
        self.mydb = mysql.connector.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            port=int(self.config['port']),
            autocommit=bool(self.config['autocommit'])
        )
        
        # set cursor
        self.cur = self.mydb.cursor()
    
    def closeMySQL(self):
        # close cursor
        self.cur.close()
        # disconnect from server
        self.mydb.close()

    def preProcessDbTables(self):
        self.createTableIfNecessary()
        self.openMySQL()
        # modify index (get last idx)
        last_id = 1
        try:
            self.cur.execute("SELECT MAX(id) FROM " + self.table_name)
            found_ids = self.cur.fetchall()
            if len(found_ids) > 0:
                last_id = int(found_ids[0][0])
        except:
            last_id = 1
        
        self.cur.execute("ALTER TABLE " + self.table_name + " AUTO_INCREMENT = " + str(last_id))
        
        self.closeMySQL()

    def getActiveTableElements(self, minimum_listings_age=10):
        # select listings
        self.openMySQL()
        listings = pd.read_sql('SELECT * FROM ' + self.table_name, con=self.mydb)

        # get only active listings
        active_listings = listings[listings['active'] == 1]
        # current date
        curDateStr = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        curDate = datetime.datetime.strptime(curDateStr, "%Y-%m-%d")
        
        # current date minus x days
        compDate = curDate - datetime.timedelta(days=minimum_listings_age)

        # find listings older than
        active_listings = listings[pd.to_datetime(listings['in_db_since']) < compDate]

        # get urls of active and older listings
        ids = active_listings['id'].tolist()
        urls = active_listings['url'].tolist()

        # check if listing is still available
        for idx in range(len(urls)):
            url = urls[idx]
            response = requests.get(url)
            if response.status_code != 200:
                self.cur.execute("UPDATE " + self.table_name + " SET active_status = 0 WHERE ID = " + str(ids[idx]) + '')

        self.closeMySQL()

    def createTableIfNecessary(self):
        self.openMySQL()
        # check if table exists
        self.cur.execute("SELECT * FROM information_schema.tables WHERE table_name = '" + self.table_name + "'")
        result = self.cur.fetchone()
        # if it does not exist create table
        if result is None and self.table_columns is not None:
            create_str =  ' (' + ', '.join([key + ' ' + self.table_columns[key] for key in self.table_columns.keys()]) + ')'
            self.cur.execute("CREATE TABLE " + self.table_name + create_str)
        
        self.closeMySQL()
    
    def querySql(self, query):
        self.cur.execute(query)
        try:
            return self.cur.fetchall()
        except:
            return None