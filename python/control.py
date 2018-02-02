import database
import relay_driver
import time

fanIndx=0
coolIndx=1
heatIndx=2

db = database.thermoDB('thermostat.db',debug=False)

def heat():
	db.setRelayStatus(coolIndx,False)
	db.setRelayStatus(heatIndx,True)
	db.setRelayStatus(fanIndx,True)

def cool():
	db.setRelayStatus(coolIndx,True)
	db.setRelayStatus(heatIndx,False)
	db.setRelayStatus(fanIndx,True)

def fan():
	db.setRelayStatus(coolIndx,False)
	db.setRelayStatus(heatIndx,False)
	db.setRelayStatus(fanIndx,True)

def off(fan_overide):
	db.setRelayStatus(coolIndx,False)
	db.setRelayStatus(heatIndx,False)
	if fan_overide:
		db.setRelayStatus(fanIndx,True)
	else:
		db.setRelayStatus(fanIndx,False)

def serviceSchedule(sch):
	if sch['enable']:
		db.setSystem(sch['system_enable'],sch['fan_overide'],sch['drift'],sch['id'])
		db.setDesiredTemp(sch['desiredTemp'])
		return sch['id']

def serviceRelays(status):
	if status['enable'] and status['currentTemp']['temp']>0.0 and status['desiredTemp']['temp']>0.0:
		if status['currentTemp']['temp']>(status['desiredTemp']['temp']+status['drift']):
			cool()
		elif status['currentTemp']['temp']<(status['desiredTemp']['temp']-status['drift']):
			heat()
		else:
			off(status['fan_overide'])
	else:
		off(status['fan_overide'])

	if [e for e in status['relays'] if e['desc']=='Fan'][0]['status']:
		rd.pinOn(rd.fanPin)
	else:
		rd.pinOff(rd.fanPin)

	if [e for e in status['relays'] if e['desc']=='Cool'][0]['status']:
		rd.pinOn(rd.coolPin)
	else:
		rd.pinOff(rd.coolPin)

	if [e for e in status['relays'] if e['desc']=='Heat'][0]['status']:
		rd.pinOn(rd.heatPin)
	else:
		rd.pinOff(rd.heatPin)

rd = relay_driver.driver()
lastSystemUpdate=0

while True:
	if lastSystemUpdate != db.getCurrentSchedule()['id']:
		lastSystemUpdate=serviceSchedule(db.getCurrentSchedule())

	serviceRelays(db.getSystemStatus())

	time.sleep(1)
