import sys
sys.path.append('lib')
from Adafruit_RA8875 import *
from time import sleep
import CHIP_IO.GPIO as GPIO
import CHIP_IO.OverlayManager as OM

# GPIO.toggle_debug()

RA8875_INT = 'XIO-P1'
RA8875_CS = 'XIO-P2'
RA8875_RESET = 'XIO-P3'

def handleInterrupt(channel):
	# GPIO.remove_event_detect(channel)
	print str(channel)
	while tft.touched():
		print "Touch event detected!"
		tft.fillScreen(RA8875_RED)
		point = tft.touchRead()
		print point
	sleep(3)
	tft.fillScreen(RA8875_GREEN)
	# GPIO.add_event_detect(RA8875_INT, GPIO.FALLING, callback=handleInterrupt, bouncetime=300)

OM.load('SPI2')
tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET)

print "RA8875 start"

# /* Initialise the display using 'RA8875_480x272' or 'RA8875_800x480' */
if not tft.begin(RA8875sizes.RA8875_800x480):
	print "RA8875 Not Found!"
	raise

print "Found RA8875"

tft.displayOn(True)
tft.GPIOX(True)      # Enable TFT - display enable tied to GPIOX
tft.PWM1config(True, RA8875_PWM_CLK_DIV1024) # PWM output for backlight
tft.PWM1out(255)
# With hardware accelleration this is instant
tft.fillScreen(RA8875_GREEN)

tft.touchEnable(True)

GPIO.setup(RA8875_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(RA8875_INT, GPIO.FALLING, callback=handleInterrupt, bouncetime=300)

while(True):
	try:
		print 'ok'
		sleep(5)
	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()