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
	'screenNext': 0
}

def handleInterrupt(channel):
	global status
	while not GPIO.input(RA8875_INT):
		if tft.touched():
			point = tft.touchRead()
			print point
			if status['screen'] == screen.main:
				status['screenNext'] = screen.menu
			elif status['screen'] == screen.menu:
				status['screenNext'] = screen.main


def renderMainScreen(data):
	global status
	status['screen'] = screen.main
	# may need to monitor wait signal in textMode
	tft.textMode()
	tft.textSetCursor(0,0)
	tft.textColor(RA8875_WHITE,RA8875_BLUE)
	tft.textWrite('Test',0)

def renderMenuScreen(data):
	global status
	status['screen'] = screen.menu
	tft.fillScreen(RA8875_RED)
	

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
GPIO.add_event_detect(RA8875_INT, GPIO.FALLING, callback=handleInterrupt, bouncetime=300)

while True:
	try:
		if status['screen'] != status['screenNext']:
			if status['screenNext'] == screen.main:
				data = {}
				renderMainScreen(data)
			elif status['screenNext'] == screen.menu:
				data = {}
				renderMenuScreen(data)

	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()