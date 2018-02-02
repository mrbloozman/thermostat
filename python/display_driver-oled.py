import sys
sys.path.append('lib')
from Adafruit_SSD1306 import *
from img import *
from time import sleep, strftime
import CHIP_IO.OverlayManager as OM
import database

OM.load("CUST","overlays/chip-i2c1.dtbo")
OM.get_custom_loaded()

db = database.thermoDB('thermostat.db',debug=False)

fans=bitSwapList([fan1,fan2,fan3])
flames=bitSwapList([flame1,flame2,flame3])
flakes=bitSwapList([flake1,flake2,flake3])
jedi=bitSwapList([jedi])[0]
makey=bitSwapList([makey])[0]

OLED_RESET = 4
DEVICE_ADDRESS = 0x3c      #7 bit address (will be left shifted to add the read write bit)

display = SSD1306(OLED_RESET)
display.begin(SSD1306_SWITCHCAPVCC,DEVICE_ADDRESS)
display.display()	# show splashscreen
sleep(2)
display.clearDisplay()   # clears the screen and buffer

while True:
	date = strftime('%b %d')
	time = strftime('%I:%M %p')

	status = db.getSystemStatus()

	display.setCursor(0,0)
	display.setTextColor(WHITE,BLACK)
	display.setTextSize(1)
	display.prnt(date)

	display.setCursor(SSD1306_LCDWIDTH-60,0)
	display.setTextSize(2)
	display.prnt('%3.1f'%(status['currentTemp']['temp'],) + chr(248))

	display.setCursor(0,9)
	display.setTextSize(1)
	display.prnt(time)

	if status['enable'] & (status['desiredTemp']['temp']>0.0) & (status['currentTemp']['temp']>0.0):
		display.setCursor(64,32)
		display.setTextSize(3)
		display.prnt('%d'%(status['desiredTemp']['temp'],) + chr(248))

		if [e for e in status['relays'] if e['desc']=='Heat'][0]['status']:
			for f in flames:
				display.drawBitmap(8, 24, f, 32, 32, WHITE)
				display.display()
				display.drawBitmap(8, 24, f, 32, 32, BLACK)
		elif [e for e in status['relays'] if e['desc']=='Cool'][0]['status']:
			for f in flakes:
				display.drawBitmap(8, 24, f, 32, 32, WHITE)
				display.display()
				display.drawBitmap(8, 24, f, 32, 32, BLACK)
		elif [e for e in status['relays'] if e['desc']=='Fan'][0]['status']:
			for f in fans:
				display.drawBitmap(8, 24, f, 32, 32, WHITE)
				display.display()
				display.drawBitmap(8, 24, f, 32, 32, BLACK)
		else:
			display.drawBitmap(4, 16, makey, 48, 51, WHITE)
			display.display()
			display.drawBitmap(4, 16, makey, 48, 51, BLACK)
	elif [e for e in status['relays'] if e['desc']=='Fan'][0]['status']:
		for f in fans:
			display.drawBitmap(8, 24, f, 32, 32, WHITE)
			display.display()
			display.drawBitmap(8, 24, f, 32, 32, BLACK)
	else:
		display.drawBitmap(40, 16, jedi, 48, 48, WHITE)
		display.display()
		display.drawBitmap(40, 16, jedi, 48, 48, BLACK)