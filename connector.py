from mysql.connector import connect
import json
from os import path

def getSettings():
    if path.exists('scraper.conf'):
        with open('scraper.conf') as file:
            lines = file.read().splitlines()
            settings = json.loads(('{"'+'","'.join(lines)+'"}').replace('=','":"'))
            return settings
    else:
        return None

SETTINGS = getSettings()

mydb = connect(
        host=SETTINGS['dbHost'],
        user=SETTINGS['dbUser'],
        passwd=SETTINGS['dbPass']
        )


mycursor = mydb.cursor()
mycursor.execute('CREATE DATABASE '+SETTINGS['dbName'])

mydb = connect(
        host=SETTINGS['dbHost'],
        user=SETTINGS['dbUser'],
        passwd=SETTINGS['dbPass'],
        database=SETTINGS['dbName']
        )
mycursor = mydb.cursor()

mycursor.execute('CREATE TABLE '+SETTINGS['empTable']+' (id INT AUTO_INCREMENT PRIMARY KEY,\
connection_id INT(11),\
connection_name VARCHAR(255),\
title VARCHAR(255),\
address VARCHAR(255),\
cur_comp VARCHAR(255),\
connection_email VARCHAR(255),\
connection_phone VARCHAR(255))')

mycursor.execute('CREATE TABLE '+SETTINGS['compTable']+' (id INT AUTO_INCREMENT PRIMARY KEY,\
connection_id INT(11),\
company VARCHAR(255),\
company_location VARCHAR(255),\
job_title VARCHAR(255),\
start_date VARCHAR(255),\
end_date VARCHAR(255))')

mycursor.execute('CREATE TABLE '+SETTINGS['eduTable']+' (id INT AUTO_INCREMENT PRIMARY KEY,\
connection_id INT(11),\
school VARCHAR(255),\
degree VARCHAR(255),\
grade VARCHAR(255),\
start_date VARCHAR(255),\
end_date VARCHAR(255))')
