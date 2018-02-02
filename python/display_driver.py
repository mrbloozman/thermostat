import sys
sys.path.append('lib')
from Adafruit_RA8875 import *
from time import sleep
import CHIP_IO.GPIO as GPIO
import CHIP_IO.OverlayManager as OM
import enum

OM.load('SPI2')

RA8875_INT = 'XIO-P1'
RA8875_CS = 'XIO-P2'
RA8875_RESET = 'XIO-P3'

class screen(enum.Enum):
	main = 0
	menu = 1

status = {
	'screen': -1,
	'screenNext': screen.main,
	'touchPoint':{},
	'message': 'startup'
}

def handleInterrupt(channel):
	print 'handleInterrupt(' + channel + ')'
	global status
	while tft.touched():
		status['touchPoint'] = tft.touchRead()
		print status['touchPoint']
		if status['screen'] == screen.main:
			status['screenNext'] = screen.menu
		elif status['screen'] == screen.menu:
			if status['touchPoint']['x'] < int(1024/3) and status['touchPoint']['y'] < 1024/2:
				status['message'] = 'touched button 1'
			elif status['touchPoint']['x'] < int(2*1024/3) and status['touchPoint']['y'] < 1024/2:
				status['message'] = 'touched button 2'
			elif status['touchPoint']['y'] < 1024/2:
				status['message'] = 'touched button 3'
			elif status['touchPoint']['x'] < int(1024/3) and status['touchPoint']['y'] >= 1024/2:
				status['message'] = 'touched button 4'
			elif status['touchPoint']['x'] < int(2*1024/3) and status['touchPoint']['y'] >= 1024/2:
				status['message'] = 'touched button 5'
			elif status['touchPoint']['y'] >= 1024/2:
				status['message'] = 'touched button 6'
			else:
				status['message'] = 'no button touched'
			status['screenNext'] = screen.main
		


def renderMainScreen(data):
	print 'renderMainScreen(' + str(data) + ')'
	global status
	status['screen'] = screen.main
	tft.fillScreen(RA8875_BLUE)
	# may need to monitor wait signal in textMode
	tft.textMode()
	tft.textEnlarge(3)
	tft.textColor(RA8875_WHITE,RA8875_BLUE)
	tft.textSetCursor(0,0)
	tft.textWrite(status['message'],0)
	tft.graphicsMode()

def renderMenuScreen(data):
	print 'renderMenuScreen(' + str(data) + ')'
	global status
	status['screen'] = screen.menu
	tft.fillScreen(RA8875_RED)
	tft.drawRect(0, 0, int(800/3), 240, RA8875_YELLOW)
	tft.drawRect(int(800/3), 0, int(800/3), 240, RA8875_YELLOW)
	tft.drawRect(int(2*800/3), 0, int(800/3), 240, RA8875_YELLOW)
	tft.drawRect(0, 240, int(800/3), 239, RA8875_YELLOW)
	tft.drawRect(int(800/3), 240, int(800/3), 239, RA8875_YELLOW)
	tft.drawRect(int(2*800/3), 240, int(800/3), 239, RA8875_YELLOW)
	

tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET)

if not tft.begin(RA8875sizes.RA8875_800x480):
	print "RA8875 Not Found!"
	raise

tft.displayOn(True)
tft.GPIOX(True)      # Enable TFT - display enable tied to GPIOX
tft.PWM1config(True, RA8875_PWM_CLK_DIV1024) # PWM output for backlight
tft.PWM1out(255)

tft.fillScreen(RA8875_BLUE)

tft.touchEnable(True)

GPIO.setup(RA8875_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.add_event_detect(RA8875_INT, GPIO.FALLING, callback=handleInterrupt, bouncetime=300)

while True:
	try:
		print 'INT PIN: ' + str(GPIO.input(RA8875_INT))
		print 'INTC1: ' + hex(tft.readReg(RA8875_INTC1))
		print 'INTC2: ' + hex(tft.readReg(RA8875_INTC2))
		if GPIO.input(RA8875_INT)==0:
			handleInterrupt(RA8875_INT)
		if status['screen'] != status['screenNext']:
			if status['screenNext'] == screen.main:
				data = {}
				renderMainScreen(data)
			elif status['screenNext'] == screen.menu:
				data = {}
				renderMenuScreen(data)

		sleep(1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()