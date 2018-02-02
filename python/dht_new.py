import CHIP_IO.GPIO as GPIO
import time

data_pin = 'XIO-P5'
max_cycles = 200

pulse_pin = 'XIO-P6'

def delayMilliSeconds(ms):
	time.sleep(float(ms)/1000.0)

def delayMicroSeconds(us):
	time.sleep(float(us)/1000000.0)

def pulseSetupPin(pin):
	GPIO.setup(pin,GPIO.OUT)
	GPIO.output(pin,GPIO.LOW)

def pulsePin(pin,us):
	GPIO.output(pin,GPIO.HIGH)
	GPIO.output(pin,GPIO.LOW)


def waitForDownSlope():
	cycle = 0
	while (GPIO.input(data_pin)) and (cycle < max_cycles):
		cycle = cycle+1
		delayMicroSeconds(1)
	if cycle==max_cycles:
		return False
	print 'Down read in ' + str(cycle) + ' cycles'
	return True

def waitForUpSlope():
	cycle = 0
	while (not GPIO.input(data_pin)) and (cycle < max_cycles):
		cycle = cycle+1
		delayMicroSeconds(1)
	if cycle==max_cycles:
		return False
	print 'Up read in ' + str(cycle) + ' cycles'
	return True

def readSensor():
	print 'start'
	# assuming line starts high (it should because of pullup)
	# MCU start signal
	GPIO.setup(data_pin,GPIO.OUT)
	GPIO.output(data_pin,GPIO.LOW)
	# time.sleep(18.0/1000.0)
	delayMilliSeconds(20)

	# listen for response from DHT
	GPIO.cleanup()
	GPIO.setup(data_pin,GPIO.IN)
	delayMicroSeconds(20)
	if waitForUpSlope():
		pass
	else:
		print 'Line not pulled high'
		return False

	if waitForDownSlope():
		pass
	else:
		print 'Response signal (80us low) not received from DHT!'
		return False
	
	if waitForUpSlope():
		pass
	else:
		print 'Response signal (80us high) not received from DHT!'
		return False

	# listen for data
	if waitForDownSlope():
		pass
	else:
		print 'Response signal (50us low) not received from DHT!'
		return False

	if waitForUpSlope():
		delayMicroSeconds(50)
		bit = GPIO.input(data_pin)
		print bit
		if waitForDownSlope():
			pass
		else:
			print 'Response signal (50us low) not received from DHT!'
			return False
	else:
		print 'Bit not received from DHT!'
		return False



	# listen for data
	# bit = True
	# for b in range(40):
	# 	if bit:
	# 		waitForDownSlope()
	# 	waitForUpSlope()
	# 	delayMicroSeconds(50)
	# 	bit = GPIO.input(data_pin)
	# 	print bit

	time.sleep(1)
	GPIO.cleanup()
	GPIO.setup(data_pin,GPIO.OUT)
	GPIO.output(data_pin,GPIO.HIGH)

	print 'done'
	return True

# readSensor()
pulseSetupPin(pulse_pin)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
GPIO.output(pulse_pin,GPIO.HIGH)
GPIO.output(pulse_pin,GPIO.LOW)
