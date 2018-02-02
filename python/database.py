import sqlite3
import os.path
import time
import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class thermoDB:
	def __init__(self,f,debug=False):
		self.debug=debug
		if self.debug:
			print 'thermoDB('+str(f)+')'

		if os.path.isfile(f):
			self.conn = sqlite3.connect(f)
			self.conn.row_factory = dict_factory
			self.c = self.conn.cursor()
		else:
			self.conn = sqlite3.connect(f)
			self.conn.row_factory = dict_factory
			self.c = self.conn.cursor()
			self.mkDB()

	def mkDB(self):
		if self.debug:
			print 'mkDB()'

		t=int(time.time())

		# status
		self.c.execute("CREATE TABLE status (id integer primary key, desc text)")
		self.c.execute("INSERT INTO status VALUES(0,'OFF')")
		self.c.execute("INSERT INTO status VALUES(1,'ON')")
		self.conn.commit()

		# relays
		self.c.execute("CREATE TABLE relays (id integer primary key, desc text, pin text, status integer)")
		self.c.execute("INSERT INTO relays VALUES(0,'Fan','XIO-P3',0)")
		self.c.execute("INSERT INTO relays VALUES(1,'Cool','XIO-P1',0)")
		self.c.execute("INSERT INTO relays VALUES(2,'Heat','XIO-P2',0)")
		self.conn.commit()

		# relays_view
		self.c.execute("CREATE VIEW relays_view as SELECT relays.*, status.desc as status_desc FROM relays, status WHERE relays.status=status.id")

		# temp
		self.c.execute("CREATE TABLE temp (timestamp integer primary key, temp real)")
		self.c.execute("INSERT INTO temp VALUES(?,?)",(t,0.0))
		self.conn.commit()

		# temp_view
		self.c.execute("CREATE VIEW temp_view as SELECT *, datetime(timestamp) as timestamp_desc from temp")

		# desiredTemp
		self.c.execute("CREATE TABLE desiredTemp (timestamp integer primary key, temp real)")
		self.c.execute("INSERT INTO desiredTemp VALUES(?,?)",(t,0.0))
		self.conn.commit()

		# desiredTemp_view
		self.c.execute("CREATE VIEW desiredTemp_view as SELECT *, datetime(timestamp) as timestamp_desc from desiredTemp")

		# system
		self.c.execute("CREATE TABLE system (timestamp integer primary key, enable integer, fan_overide integer, drift real, schedule integer)")
		self.c.execute("INSERT INTO system VALUES(?,?,?,?,?)",(t,0,0,1.0,0))
		self.conn.commit()

		# system_view
		self.c.execute("CREATE VIEW system_view as SELECT *, datetime(timestamp) as timestamp_desc, status.desc as enable_desc FROM system, status WHERE system.enable=status.id")

		# schedule
		self.c.execute("CREATE TABLE schedule (id integer primary key, enable integer, day integer, time integer, system_enable integer, fan_overide integer, drift real, desiredTemp real)")
		self.c.execute("INSERT INTO schedule VALUES(0,0,0,0,0,0,0.0,0.0)")
		self.conn.commit()

		if self.debug:
			ts = ['status','relays','temp','desiredTemp','system', 'schedule']
			for tbl in ts:
				sql='SELECT * FROM '+tbl
				print sql
				for r in self.c.execute(sql):
					print r

	def setSystem(self,enable,fan_overide,drift,schedule):
		t=int(time.time())
		if self.debug:
			print 'setSystem('+str(enable)+','+ str(fan_overide) + ',' + str(drift) + ',' + str(schedule) + ') at ' + str(t)
		if self.getLastSystem()['timestamp']==t:
			self.c.execute("DELETE FROM system WHERE timestamp=?",(t,))
			self.conn.commit()
		self.c.execute("INSERT INTO system VALUES(?,?,?,?,?)",(t,int(enable),int(fan_overide),float(drift),int(schedule)))
		self.conn.commit()

	def setSystemEnable(self,enable):
		if self.debug:
			print 'setSystemEnable(' + str(enable) + ')'
		s = self.getLastSystem()
		self.setSystem(int(enable),s['fan_overide'],s['drift'],s['schedule'])

	def setSystemFan(self,fan_overide):
		if self.debug:
			print 'setSystemFan(' + str(fan_overide) + ')'
		s = self.getLastSystem()
		self.setSystem(s['enable'],int(fan_overide),s['drift'],s['schedule'])

	def getLastSystem(self):
		if self.debug:
			print 'getLastSystem()'
		self.c.execute("SELECT * FROM system_view ORDER BY timestamp desc LIMIT 1")
		return self.c.fetchone()

	def getSystemStatus(self):
		if self.debug:
			print 'getSystemStatus()'
		system = self.getLastSystem()
		relays = self.getRelays()
		desiredTemp = self.getLastDesiredTemp()
		currentTemp = self.getLastTemp()
		system['relays'] = relays
		system['desiredTemp'] = desiredTemp
		system['currentTemp'] = currentTemp
		return system

	def setTemp(self,temp):
		t=int(time.time())
		if self.debug:
			print 'setTemp('+str(temp)+') at ' + str(t)
		if self.getLastTemp()['timestamp']!=t:
			self.c.execute("INSERT INTO temp VALUES(?,?)",(t,float(temp)))
			self.conn.commit()

	def setDesiredTemp(self,temp):
		t=int(time.time())
		if self.debug:
			print 'setDesiredTemp('+str(temp)+') at ' + str(t)
		if self.getLastDesiredTemp()['timestamp']!=t:
			self.c.execute("INSERT INTO desiredTemp VALUES(?,?)",(t,float(temp)))
			self.conn.commit()

	def getLastTemp(self):
		if self.debug:
			print 'getLastTemp()'
		self.c.execute("SELECT * FROM temp_view ORDER BY timestamp desc LIMIT 1")
		return self.c.fetchone()

	def getLastDesiredTemp(self):
		if self.debug:
			print 'getLastDesiredTemp()'
		self.c.execute("SELECT * FROM desiredTemp_view ORDER BY timestamp desc LIMIT 1")
		return self.c.fetchone()

	def getRelay(self,id):
		if self.debug:
			print 'getRelay('+str(id)+')'
		self.c.execute("SELECT * FROM relays WHERE id=?",(id,))
		return self.c.fetchone()

	def getRelays(self):
		if self.debug:
			print 'getRelays()'
		self.c.execute("SELECT * FROM relays_view")
		return self.c.fetchall()

	def setRelayPin(self,id,pin):
		if self.debug:
			print 'setRelayPin('+str(id)+','+str(pin)+')'
		self.c.execute("UPDATE relays SET pin=? WHERE id=?",(pin,id))
		self.conn.commit()

	def setRelayStatus(self,id,status):
		if self.debug:
			print 'setRelayStatus('+str(id)+','+str(status)+')'
		self.c.execute("UPDATE relays SET status=? WHERE id=?",(status,id))
		self.conn.commit()

	def getSchedules(self):
		if self.debug:
			print 'getSchedules()'
		self.c.execute("SELECT * FROM schedule")
		return self.c.fetchall()

	def getCurrentSchedule(self):
		if self.debug:
			print 'getCurrentSchedule()'
		dt = datetime.datetime.now()
		d = dt.weekday()
		t = int(dt.strftime('%H%M'))

		for i in range(7):
			x = (d-i)%7
			if i==0:
				y=t
			else:
				y=2359
			self.c.execute("SELECT * FROM schedule WHERE day=? AND time<=? ORDER BY day desc, time desc",(x,y))
			r = self.c.fetchone()
			if r:
				return r

	def putSchedule(self, enable, day, time, system_enable, fan_overide, drift, desiredTemp):
		if self.debug:
			print 'putSchedule('+str(enable)+','+str(day)+','+str(time)+','+str(system_enable)+','+str(fan_overide)+','+str(drift)+','+str(desiredTemp)+')'
		self.c.execute("SELECT max(id) as id FROM schedule")
		pk = int(self.c.fetchone()['id'])+1
		self.c.execute("INSERT INTO schedule VALUES(?,?,?,?,?,?,?,?)",(pk,int(enable),int(day),int(time),int(system_enable),int(fan_overide),float(drift),float(desiredTemp)))
		self.conn.commit()

	def updateSchedule(self, id, enable, day, time, system_enable, fan_overide, drift, desiredTemp):
		if self.debug:
			print 'updateSchedule('+str(id)+','+str(enable)+','+str(day)+','+str(time)+','+str(system_enable)+','+str(fan_overide)+','+str(drift)+','+str(desiredTemp)+')'
		self.c.execute("UPDATE schedule SET enable=?, day=?, time=?, system_enable=?, fan_overide=?, drift=?, desiredTemp=? WHERE id=?",(int(enable),int(day),int(time),int(system_enable),int(fan_overide),float(drift),float(desiredTemp),int(id)))
		self.conn.commit()

	def deleteSchedule(self, id):
		if self.debug:
			print 'deleteSchedule('+str(id)+')'
		self.c.execute("DELETE FROM schedule WHERE id=?",(int(id),))
		self.conn.commit()

# 	def test(self):
# 		# self.updateSchedule(0, 1, 5, 2000, 1, 1, 1.0, 78.6)
# 		print self.getCurrentSchedule()
# 		self.conn.close()

# db = thermoDB('thermostat.db',debug=True)
# db.test()