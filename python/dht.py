import CHIP_IO.GPIO as GPIO
from datetime import datetime
from datetime import timedelta
import time
import sys, traceback

start_time = datetime.now()

# returns the elapsed milliseconds since the start of the program
def millis():
	dt = datetime.now() - start_time
	ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
	return ms

def delay(ms):
	# print 'delay: ' + str(ms)
	# start = millis()
	time.sleep(float(ms)/1000.0)
	# print 'delayed: ' + str(millis()-start)

def delayMicroseconds(us):
	# print 'delayMicroseconds: ' + str(us)
	# start = millis()
	time.sleep(float(us)/1000000.0)
	# print 'delayed: ' + str(millis()-start)

MIN_INTERVAL=2000
# Define types of sensors.
DHT11=11
DHT22=22
DHT21=21
AM2301=21

class DHT:
	def __init__(self,pin,type,count):
		self.data=[0,0,0,0,0]
		self._pin = pin
		self._type = type
		self._maxcycles = count


	def begin(self):
		#set up the pins!
		GPIO.setup(self._pin, GPIO.IN)
  # Using this value makes sure that millis() - lastreadtime will be
  # >= MIN_INTERVAL right away. Note that this assignment wraps around,
  # but so will the subtraction.
		self._lastreadtime = -MIN_INTERVAL
		print "Max clock cycles: "+ str(self._maxcycles)
		print "Pin: "+self._pin

#boolean S == Scale.  True == Fahrenheit; False == Celcius
	def readTemperature(self,S,force):
		f = 0.0

		if self.read(force):
			if self._type==DHT11:
				f = self.data[2]
				if S:
					f = self.convertCtoF(f)
			if self._type in [DHT21,DHT22]:
				f = self.data[2] & 0x7F
				f *= 256
				f += self.data[3]
				f *= 0.1
				if (self.data[2] & 0x80):
					f *= -1
				if S:
					f = self.convertCtoF(f)
		return f

	def convertCtoF(self,c):
		return float(c*1.8+32)

	def convertFtoC(self,f):
		return float((f-32)*0.55555)

	def readHumidity(self,force):
		f = 0.0
		if self.read():
			if self._type==DHT11:
				f=self.data[0]
			if self._type in [DHT21,DHT22]:
				f = data[0]
				f *= 256
				f += data[1]
				f *= 0.1
		return f;

#boolean isFahrenheit: True == Fahrenheit; False == Celcius
	def computeHeatIndex(self, temperature, percentHumidity, isFahrenheit):
  # Using both Rothfusz and Steadman's equations
  # http:#www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
		hi=0.0
		if not(isFahrenheit):
			temperature=self.convertCtoF(temperature)

		hi = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + (percentHumidity * 0.094))

		if (hi > 79):
			hi = (-42.379 +
			 2.04901523 * temperature +
			10.14333127 * percentHumidity +
			-0.22475541 * temperature*percentHumidity +
			-0.00683783 * pow(temperature, 2) +
			-0.05481717 * pow(percentHumidity, 2) +
			 0.00122874 * pow(temperature, 2) * percentHumidity +
			 0.00085282 * temperature*pow(percentHumidity, 2) +
			-0.00000199 * pow(temperature, 2) * pow(percentHumidity, 2))

		if ((percentHumidity < 13) and (temperature >= 80.0) and (temperature <= 112.0)):
			hi -= ((13.0 - percentHumidity) * 0.25) * sqrt((17.0 - abs(temperature - 95.0)) * 0.05882)
		elif ((percentHumidity > 85.0) and (temperature >= 80.0) and(temperature <= 87.0)):
			hi += ((percentHumidity - 85.0) * 0.1) * ((87.0 - temperature) * 0.2)

		if isFahrenheit:
			return hi
		else:
			return self.convertFtoC(hi)

	def read(self, force):
  # Check if sensor was read less than two seconds ago and return early
  # to use last reading.
		currenttime = millis()
		if (not(force) and ((currenttime - self._lastreadtime) < 2000)):
			return self._lastresult # return last correct measurement
  
		self._lastreadtime = currenttime

  # Reset 40 bits of received data to zero.
		self.data[0] = self.data[1] = self.data[2] = self.data[3] = self.data[4] = 0

  # Send start signal.  See DHT datasheet for full signal diagram:
  #   http:#www.adafruit.com/datasheets/Digital%20humidity%20and%20temperature%20sensor%20AM2302.pdf

  # Go into high impedence state to let pull-up raise data line level and
  # start the reading process.
  		GPIO.cleanup()
  		GPIO.setup(self._pin, GPIO.OUT)
		GPIO.output(self._pin, GPIO.HIGH)
		delay(250)

  # First set data line low for 20 milliseconds.
		GPIO.output(self._pin, GPIO.LOW)
		delay(50)

		cycles=[]

		# Turn off interrupts temporarily because the next sections are timing critical
		# and we don't want any interruptions.
		# InterruptLock lock;

		# End the start signal by setting data line high for 40 microseconds.
		GPIO.output(self._pin, GPIO.HIGH)
		delayMicroseconds(40)

		# Now start reading the data line to get the value from the DHT sensor.
		GPIO.cleanup()
		GPIO.setup(self._pin, GPIO.IN)
		delayMicroseconds(10)  # Delay a bit to let sensor pull data line low.

		# while GPIO.input(self._pin):
		# 	print "wait..."

		# First expect a low signal for ~80 microseconds followed by a high signal
		# for ~80 microseconds again.
		if (self.expectPulse(GPIO.LOW) == 0):
			print "Timeout waiting for start signal low pulse.\n"
			self._lastresult = False
			return self._lastresult

		if (self.expectPulse(GPIO.HIGH) == 0):
			print "Timeout waiting for start signal high pulse.\n"
			self._lastresult = False
			return self._lastresult

		# Now read the 40 bits sent by the sensor.  Each bit is sent as a 50
		# microsecond low pulse followed by a variable length high pulse.  If the
		# high pulse is ~28 microseconds then it's a 0 and if it's ~70 microseconds
		# then it's a 1.  We measure the cycle count of the initial 50us low pulse
		# and use that to compare to the cycle count of the high pulse to determine
		# if the bit is a 0 (high state cycle count < low state cycle count), or a
		# 1 (high state cycle count > low state cycle count). Note that for speed all
		# the pulses are read into a array and then examined in a later step.
		for i in range(0,80,2):
			cycles.append(self.expectPulse(GPIO.LOW))
			cycles.append(self.expectPulse(GPIO.HIGH))

	 	 # Timing critical code is now complete.

	  # Inspect pulses and determine which ones are 0 (high state cycle count < low
	  # state cycle count), or 1 (high state cycle count > low state cycle count).
		for i in range(40):
			lowCycles  = cycles[2*i]
			highCycles = cycles[2*i+1]
			if ((lowCycles == 0) and (highCycles == 0)):
				print "Timeout waiting for pulse.\n"
				self._lastresult = False
				return self._lastresult

			self.data[i/8] <<= 1
		# Now compare the low and high cycle times to see if the bit is a 0 or 1.
			if (highCycles > lowCycles):
		  # High cycles are greater than 50us low cycle count, must be a 1.
				self.data[i/8] |= 1
		
		# Else high cycles are less than (or equal to, a weird case) the 50us low
		# cycle count so this must be a zero.  Nothing needs to be changed in the
		# stored data.
	  

		print "Received:\n"
		print hex(self.data[0])+", "
		print hex(self.data[1])+", "
		print hex(self.data[2])+", "
		print hex(self.data[3])+", "
		print hex(self.data[4])+" =? "
		print hex((self.data[0] + self.data[1] + self.data[2] + self.data[3]) & 0xFF)+"\n"

	  # Check we read 40 bits and that the checksum matches.
		if (self.data[4] == ((self.data[0] + self.data[1] + self.data[2] + self.data[3]) & 0xFF)):
			self._lastresult = True
			return self._lastresult
		else:
			print "Checksum failure!\n"
			self._lastresult = False
			return self._lastresult

# Expect the signal line to be at the specified level for a period of time and
# return a count of loop cycles spent at that level (this cycle count can be
# used to compare the relative time of two pulses).  If more than a millisecond
# ellapses without the level changing then the call fails with a 0 response.
# This is adapted from Arduino's pulseInLong function (which is only available
# in the very latest IDE versions):
#   https:#github.com/arduino/Arduino/blob/master/hardware/arduino/avr/cores/arduino/wiring_pulse.c
	def expectPulse(self, level):
		count = 0
		# print str(GPIO.input(self._pin))
		# print str(level)
		while (GPIO.input(self._pin) == level):
			count += 1
			# print str(count)
			delayMicroseconds(1)
			if (count >= self._maxcycles):
				return 0 # Exceeded timeout, fail.
		return count

try:
	dht11=DHT('XIO-P7',DHT11,1000)
	dht11.begin()
	print dht11.readTemperature(True,False)
except Exception as e:
	ex_type, ex, tb = sys.exc_info()
	traceback.print_tb(tb)
	print e
	GPIO.cleanup()

