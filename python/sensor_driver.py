import sqlite3
import requests
import database
import time

db = database.thermoDB('thermostat.db',debug=False)

sensorHost = 'http://192.168.1.120'

while True:
	r = requests.get(sensorHost+'/temp')
	j = r.json()

	# print 'Temp: ' + str(float(j['temp']))

	db.setTemp(float(j['temp']))

	time.sleep(5)
