import sys
sys.path.append('lib')
from Adafruit_RA8875 import *
from time import sleep
import CHIP_IO.GPIO as GPIO
import CHIP_IO.OverlayManager as OM

RA8875_INT = 'XIO-P1'
RA8875_CS = 'XIO-P2'
RA8875_RESET = 'XIO-P3'

OM.load('SPI2')
tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET)
tx = 0
ty = 0

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
tft.fillScreen(RA8875_WHITE)

# Play with PWM
for i in range(255,0,-5):
	tft.PWM1out(i)
	sleep(0.01)

for i in range(0,255,5):
	tft.PWM1out(i)
	sleep(0.01)

tft.PWM1out(255)

tft.fillScreen(RA8875_RED)
sleep(0.5)
tft.fillScreen(RA8875_YELLOW)
sleep(0.5)
tft.fillScreen(RA8875_GREEN)
sleep(0.5)
tft.fillScreen(RA8875_CYAN)
sleep(0.5)
tft.fillScreen(RA8875_MAGENTA)
sleep(0.5)
tft.fillScreen(RA8875_BLACK)

# Try some GFX acceleration!
tft.drawCircle(100, 100, 50, RA8875_BLACK)
tft.fillCircle(100, 100, 49, RA8875_GREEN)

tft.fillRect(11, 11, 398, 198, RA8875_BLUE)
tft.drawRect(10, 10, 400, 200, RA8875_GREEN)
tft.fillRoundRect(200, 10, 200, 100, 10, RA8875_RED)
tft.drawPixel(10,10,RA8875_BLACK)
tft.drawPixel(11,11,RA8875_BLACK)
tft.drawLine(10, 10, 200, 100, RA8875_RED)
tft.drawTriangle(200, 15, 250, 100, 150, 125, RA8875_BLACK)
tft.fillTriangle(200, 16, 249, 99, 151, 124, RA8875_YELLOW)
tft.drawEllipse(300, 100, 100, 40, RA8875_BLACK)
tft.fillEllipse(300, 100, 98, 38, RA8875_GREEN)
# Argument 5 (curvePart) is a 2-bit value to control each corner (select 0, 1, 2, or 3)
tft.drawCurve(50, 100, 80, 40, 2, RA8875_BLACK)  
tft.fillCurve(50, 100, 78, 38, 2, RA8875_WHITE)

GPIO.setup(RA8875_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

tft.touchEnable(True)

print "Status: " + str(tft.readStatus())
print "Waiting for touch events ..."

while(True):
	xScale = 1024.0/tft.width()
	yScale = 1024.0/tft.height()

	# /* Wait around for touch events */
	if not GPIO.input(RA8875_INT):
		if tft.touched():
			print "Touch: "
			point = tft.touchRead()
			tx = point['x']
			ty = point['y']
			print str(tx) + ", " + str(ty)
			# /* Draw a circle */
			tft.fillCircle((tx/xScale), (ty/yScale), 4, RA8875_WHITE)
			