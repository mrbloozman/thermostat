from flask import Flask, render_template, request
import pyjade
import database
import json
import time

# database
db = database.thermoDB('thermostat.db',debug=True)

# webapp
app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
# app.config['BASIC_AUTH_USERNAME'] = 'mark'
# app.config['BASIC_AUTH_PASSWORD'] = 'sojan123'

# basic_auth = BasicAuth(app)

# helpers
def readCheckbox(cb):
	if cb=='on' or cb=='true':
		return 1
	else:
		return 0

def readFloat(n):
	return float(n)

def readInt(n):
	return int(n)

def readTime(t):
	return int(t.replace(':',''))

def formatBool(b):
	if b:
		return 'Yes'
	else:
		return 'No'

def formatDay(d):
	days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
	return days[d]

def formatTime(t):
	return time.strftime('%I:%M %p',time.strptime(str(t),'%H%M'))

def formatDateTime(epoch):
	return time.strftime('%Y-%m-%d %I:%M %p', time.localtime(epoch))

@app.route("/")
def home():
	try:
		jSystem = db.getSystemStatus()
		jSystem['timestamp_desc'] = formatDateTime(jSystem['timestamp'])
		jSystem['currentTemp']['timestamp_desc'] = formatDateTime(jSystem['currentTemp']['timestamp'])
		jSystem['desiredTemp']['timestamp_desc'] = formatDateTime(jSystem['desiredTemp']['timestamp'])
		return render_template('home.jade',system=jSystem)
	except Exception as e:
		print(str(e))
		return str(e)

@app.route("/schedules")
def schedules():
	try:
		lSchedules = db.getSchedules()
		for s in lSchedules:
			s['enable']=formatBool(s['enable'])
			s['system_enable']=formatBool(s['system_enable'])
			s['fan_overide']=formatBool(s['fan_overide'])
			s['day']=formatDay(s['day'])
			s['time']=formatTime("{:04}".format(s['time']))
		return render_template('schedules.jade',schedules=lSchedules)
	except Exception as e:
		print(str(e))
		return str(e)

@app.route("/putSchedule",methods=['POST'])
def putSchedule():
	try:
		if request.method == 'POST':
			f = request.form
			print f
			enable = readCheckbox(f.get('enable',''))
			day = readInt(f['day'])
			time = readTime(f['time'])
			system_enable = readCheckbox(f.get('system_enable',''))
			fan_overide = readCheckbox(f.get('fan_overide',''))
			drift = readFloat(f['drift'])
			desiredTemp = readFloat(f['desiredTemp'])
			db.putSchedule(enable, day, time, system_enable, fan_overide, drift, desiredTemp)
			return schedules()
	except Exception as e:
		print(str(e))
		return str(e)

@app.route("/deleteSchedule",methods=['POST'])
def deleteSchedule():
	try:
		if request.method == 'POST':
			f = request.form
			print f
			id = readInt(f['id'])
			db.deleteSchedule(id)
			return schedules()
	except Exception as e:
		print(str(e))
		return str(e)

@app.route('/setDesiredTemp',methods=['POST'])
def setDesiredTemp():
	try:
		if request.method == 'POST':
			f = request.form
			print f
			temp = readFloat(f['temp'])
			db.setDesiredTemp(temp)
			return home()
	except Exception as e:
		print(str(e))
		return str(e)

@app.route('/setSystemEnable',methods=['POST'])
def setSystemEnable():
	try:
		if request.method == 'POST':
			f = request.form
			print f
			enable = readInt(f['enable'])
			db.setSystemEnable(enable)
			return home()
	except Exception as e:
		print(str(e))
		return str(e)

@app.route('/setSystemFan',methods=['POST'])
def setSystemFan():
	try:
		if request.method == 'POST':
			f = request.form
			print f
			fan = readInt(f['fan'])
			db.setSystemFan(fan)
			return home()
	except Exception as e:
		print(str(e))
		return str(e)



if __name__ == '__main__':
	print('*** webservRunTime ***')
	app.run(host='0.0.0.0', port=80)

