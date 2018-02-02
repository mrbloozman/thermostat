import sys
sys.path.append('lib')
from Adafruit_SSD1306 import *
from time import sleep
import random
import CHIP_IO.OverlayManager as OM

# The full path to the dtbo file needs to be specified
OM.load("CUST","overlays/chip-i2c1.dtbo")
# You can check for loading like above, but it's really just there for sameness
OM.get_custom_loaded()
# To unload, just call unload()
# OM.unload("CUST")

OLED_RESET = 4
display = SSD1306(OLED_RESET)

NUMFLAKES = 10
# XPOS = 0
# YPOS = 1
# DELTAY = 2

LOGO16_GLCD_HEIGHT = 16 
LOGO16_GLCD_WIDTH = 16 

logo16_glcd_bmp=[0b00000000, 0b11000000,
  0b00000001, 0b11000000,
  0b00000001, 0b11000000,
  0b00000011, 0b11100000,
  0b11110011, 0b11100000,
  0b11111110, 0b11111000,
  0b01111110, 0b11111111,
  0b00110011, 0b10011111,
  0b00011111, 0b11111100,
  0b00001101, 0b01110000,
  0b00011011, 0b10100000,
  0b00111111, 0b11100000,
  0b00111111, 0b11110000,
  0b01111100, 0b11110000,
  0b01110000, 0b01110000,
  0b00000000, 0b00110000]

def testdrawbitmap(bitmap, w,  h):
	# initialize
	icons=[]
	for f in range(NUMFLAKES):
		# icons[f]["XPOS"] = random.randint(0,1024) % display.width()
		# icons[f]["YPOS"] = 0
		# icons[f]["DELTAY"] = random.randint(0,1024) % 5 + 1
		icons.append({"XPOS":random.randint(0,1024) % display.width(),"YPOS":0,"DELTAY":random.randint(0,1024) % 5 + 1})

		# print str("x: ")
		# print str(icons[f]["XPOS"])
		# print str(" y: ")
		# print str(icons[f]["YPOS"])
		# print str(" dy: ")
		# print str(icons[f]["DELTAY"]) + "\n"

	while True:
		# draw each icon
		for f in range(NUMFLAKES):
			display.drawBitmap(icons[f]["XPOS"], icons[f]["YPOS"], logo16_glcd_bmp, w, h, WHITE)
		display.display()
		sleep(0.05)

		# then erase it + move it
		for f in range(NUMFLAKES):
			display.drawBitmap(icons[f]["XPOS"], icons[f]["YPOS"],  logo16_glcd_bmp, w, h, BLACK)
			# move it
			icons[f]["YPOS"] += icons[f]["DELTAY"]

			# if its gone, reinit
			if (icons[f]["YPOS"] > display.height()):
				icons[f]["XPOS"] = random.randint(0,1024) % display.width()
				icons[f]["YPOS"] = 0
				icons[f]["DELTAY"] = random.randint(0,1024) % 5 + 1

def testdrawchar():
	display.setTextSize(1)
	display.setTextColor(WHITE,BLACK)
	display.setCursor(0,0)

	for i in range(0,168):
		if (i == '\n'):
			pass
		else:
			display.write(chr(i))
			if ((i > 0) and (i % 21 == 0)):
				display.prntln('')   
	display.display()

def testdrawcircle():
	for i in range(0,display.height(),2):
		display.drawCircle(display.width()/2, display.height()/2, i, WHITE)
		display.display()

def testfillrect():
	color = 1
	for i in range(0,display.height()/2,3):
		# alternate colors
		display.fillRect(i, i, display.width()-i*2, display.height()-i*2, color%2)
		display.display()
		color+=1

def testdrawtriangle():
	for i in range(0,min(display.width(),display.height())/2,5):
		display.drawTriangle(display.width()/2, display.height()/2-i,display.width()/2-i, display.height()/2+i,display.width()/2+i, display.height()/2+i, WHITE)
		display.display()

def testfilltriangle():
	color = WHITE
	for i in range(min(display.width(),display.height())/2,0,5):
		display.fillTriangle(display.width()/2, display.height()/2-i,display.width()/2-i, display.height()/2+i,display.width()/2+i, display.height()/2+i, WHITE)
		if (color == WHITE):
			color = BLACK
		else:
			color = WHITE
		display.display()

def testdrawroundrect():
	for i in range(0,display.height()/2-2,2):
		display.drawRoundRect(i, i, display.width()-2*i, display.height()-2*i, display.height()/4, WHITE)
		display.display()

def testfillroundrect():
	color = WHITE
	for i in range(0,display.height()/2-2,2):
		display.fillRoundRect(i, i, display.width()-2*i, display.height()-2*i, display.height()/4, color)
		if (color == WHITE):
			color = BLACK
		else:
			color = WHITE
		display.display()

def testdrawrect():
	for i in range(0,display.height()/2,2):
		display.drawRect(i, i, display.width()-2*i, display.height()-2*i, WHITE)
		display.display()

def testdrawline():
	for i in range(0,display.width(),4):
		display.drawLine(0, 0, i, display.height()-1, WHITE)
		display.display()

	for i in range(0,display.height(),4):
		display.drawLine(0, 0, display.width()-1, i, WHITE)
		display.display()

	sleep(0.25)

	display.clearDisplay()
	for i in range(0,display.width(),4):
		display.drawLine(0, display.height()-1, i, 0, WHITE)
		display.display()
	
	for i in range(display.height()-1,0,-4):
		display.drawLine(0, display.height()-1, display.width()-1, i, WHITE)
		display.display()
	
	sleep(0.250)

	display.clearDisplay()
	for i in range(display.width()-1,0,-4):
		display.drawLine(display.width()-1, display.height()-1, i, 0, WHITE)
		display.display()
	
	for i in range(display.height()-1,0,-4):
		display.drawLine(display.width()-1, display.height()-1, 0, i, WHITE)
		display.display()
	
	sleep(0.250)

	display.clearDisplay()
	for i in range(0,display.height(),4):
		display.drawLine(display.width()-1, 0, 0, i, WHITE)
		display.display()
	
	for i in range(0,display.width(),4):
		display.drawLine(display.width()-1, 0, i, display.height()-1, WHITE) 
		display.display()
	
	sleep(0.250)
	

def testscrolltext():
	display.setTextSize(2)
	display.setTextColor(WHITE,BLACK)
	display.setCursor(10,0)
	display.clearDisplay()
	display.prntln("scroll")
	display.display()

	display.startscrollright(0x00, 0x0F)
	sleep(2)
	display.stopscroll()
	sleep(1)
	display.startscrollleft(0x00, 0x0F)
	sleep(2)
	display.stopscroll()
	sleep(1)    
	display.startscrolldiagright(0x00, 0x07)
	sleep(2)
	display.startscrolldiagleft(0x00, 0x07)
	sleep(2)
	display.stopscroll()

DEVICE_ADDRESS = 0x3c      #7 bit address (will be left shifted to add the read write bit)
display.begin(SSD1306_SWITCHCAPVCC,DEVICE_ADDRESS)
display.display()	# show splashscreen
sleep(2)
display.clearDisplay()   # clears the screen and buffer

# draw a single pixel
# display.drawPixel(10, 10, WHITE)
# display.display()
# sleep(2)
# display.clearDisplay()

# # draw many lines
# # testdrawline()
# # display.display()
# # sleep(2)
# # display.clearDisplay()

# # draw rectangles
# testdrawrect()
# display.display()
# sleep(2)
# display.clearDisplay()

# # draw multiple rectangles
# testfillrect()
# display.display()
# sleep(2)
# display.clearDisplay()

# # draw mulitple circles
# testdrawcircle()
# display.display()
# sleep(2)
# display.clearDisplay()

# # draw a white circle, 10 pixel radius
# display.fillCircle(display.width()/2, display.height()/2, 10, WHITE)
# display.display()
# sleep(2)
# display.clearDisplay()

# testdrawroundrect()
# sleep(2)
# display.clearDisplay()

# testfillroundrect()
# sleep(2)
# display.clearDisplay()

# testdrawtriangle()
# sleep(2)
# display.clearDisplay()

# testfilltriangle()
# sleep(2)
# display.clearDisplay()

# draw the first ~12 characters in the font
testdrawchar()
display.display()
sleep(2)
display.clearDisplay()

# draw scrolling text
testscrolltext()
sleep(2)
display.clearDisplay()

# text display tests
display.setTextSize(1)
display.setTextColor(WHITE,BLACK)
display.setCursor(0,0)
display.prntln("Hello, world!")
display.setTextColor(BLACK, WHITE) # 'inverted' text
display.prntln(str(3.141592))
display.setTextSize(2)
display.setTextColor(WHITE,BLACK)
# display.prnt("0x") 
display.prntln(str(0xDEADBEEF))
display.display()
sleep(2)

# miniature bitmap display
# display.clearDisplay()
# display.drawBitmap(30, 16,  logo16_glcd_bmp, 16, 16, 1)
# display.display()

# # invert the display
# display.invertDisplay(True)
# sleep(1) 
# display.invertDisplay(False)
# sleep(1) 

# # draw a bitmap icon and 'animate' movement
# display.clearDisplay()
# testdrawbitmap(logo16_glcd_bmp, LOGO16_GLCD_HEIGHT, LOGO16_GLCD_WIDTH)