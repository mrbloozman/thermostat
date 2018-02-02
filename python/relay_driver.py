import CHIP_IO.GPIO as GPIO
import database

db = database.thermoDB('thermostat.db',debug=False)

class driver:
	def __init__(self):
		self.reset()

	def pinOn(self,p):
		# print 'pinOn('+p+')'
		GPIO.output(p,GPIO.LOW)

	def pinOff(self,p):
		# print 'pinOff('+p+')'
		GPIO.output(p,GPIO.HIGH)

	def reset(self):
		status = db.getSystemStatus()
		# print status
		self.heatPin=[e for e in status['relays'] if e['desc']=='Heat'][0]['pin']
		# print heatPin
		self.coolPin=[e for e in status['relays'] if e['desc']=='Cool'][0]['pin']
		# print coolPin
		self.fanPin=[e for e in status['relays'] if e['desc']=='Fan'][0]['pin']
		# print fanPin


		GPIO.cleanup()

		GPIO.setup(self.heatPin,GPIO.OUT)
		GPIO.setup(self.coolPin,GPIO.OUT)
		GPIO.setup(self.fanPin,GPIO.OUT)

		GPIO.output(self.heatPin,GPIO.HIGH)
		GPIO.output(self.coolPin,GPIO.HIGH)
		GPIO.output(self.fanPin,GPIO.HIGH)
