import sqlite3

INIT_STRING = """CREATE TABLE IF NOT EXISTS TempData (ID text, 
temp real NOT NULL, date date NOT NULL)"""
INSERT_STRING = "INSERT INTO TempData (ID, temp, date) VALUES (?, ?, ?)"
FETCH_STRING = "SELECT from TempData WHERE ID=?"
DB = 'swarm_log.sqlite3'

class mqtt_database():
    def __init__(self, path=DB):
        self.path = path
        self.con = None
        self.cursor = None
        try:
            self.con = sqlite3.connect(self.path)
            self.cursor = self.con.cursor()
            self.cursor.execute(INIT_STRING)
            self.con.commit()
        except Exception as dbase_error:
            print(dbase_error)

    def insert_value(self, payload):
        '''
        accepts a tuple and inserts it into the database
        '''
        self.cursor.execute(INSERT_STRING, payload)
        self.con.commit()
    
    def fetch_value(self, r_value):
        '''
        param: r_value = tuple of strings to extract from 
        the database
        '''
        self.cursor.execute(FETCH_STRING, r_value)
        return self.cursor.fetchall()
    
    def close_connection(self):
        self.con.close()


