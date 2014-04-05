#!/usr/bin/python
import sqlite3
import common

class DbCreator:

    @staticmethod
    def createEmpty(filename=None):

        if None == filename:
            filename=common.Config.getDbFilename()                

        conn = sqlite3.connect(filename)

        c = conn.cursor()



        c.execute('''DROP TABLE IF EXISTS sensorinos''')
        c.execute('''CREATE TABLE sensorinos
                     (sid INTEGER PRIMARY KEY, name text, address text UNIQUE, description text, owner text, location text)''')


        c.execute('''DROP TABLE IF EXISTS services''')
        c.execute('''CREATE TABLE services
                     (serviceId INTEGER PRIMARY KEY, name text, stype text, dataType text, sid integer, state text)''')


        c.execute('''DROP TABLE IF EXISTS dataServicesLog''')
        c.execute('''CREATE TABLE dataServicesLog
                     (sid integer, serviceId integer, value text, timestamp text)''')




        # Save (commit) the changes
        conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        conn.close()

if __name__ == '__main__':
    DbCreator.createEmpty()