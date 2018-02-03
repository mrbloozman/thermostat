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

class button:
	def __init__(self,x,y,w,h,fg_color,bg_color,label,callback):
		self.x = int(x)
		self.y = int(y)
		self.w = int(w)
		self.h = int(h)
		self.fg_color = fg_color
		self.bg_color = bg_color
		self.label = label
		self.enabled = True
		self._callback = callback

	def render(self):
		if self.enabled:
			bg_color = self.bg_color
		else:
			bg_color = RA8875_BLACK
		tft.graphicsMode()
		tft.fillRect(self.x,self.y,self.w,self.h,bg_color)
		tft.drawRect(self.x,self.y,self.w,self.h,self.fg_color)
		tft.textMode()
		tft.textColor(self.fg_color,bg_color)
		tft.textSetCursor(self.x+10,self.y+int(self.h/2))
		tft.textWrite(self.label,0)
		self._active = True

	def tapped(self,touchPoint):
		if not self.enabled:
			return False
		tp = touchPoint
		nw = self.w * 1024 / tft.width()	# normalized button width
		nh = self.h * 1024 / tft.height()	# normalized button height
		nx = self.x * 1024 / tft.width()	# normalized button x position
		ny = self.y * 1024 / tft.height()	# normalized button y position
		if nx <= tp['x'] <= (nx+nw):
			if ny <= tp['y'] <= (ny+nh):
				self._callback()
				return True
			else:
				return False
		else:
			return False

class menu:
	def __init__(self,menu_id,rows,cols,button_data,fg_color,bg_color):
		self._menu_id = menu_id
		self._rows = rows
		self._cols = cols
		self._button_data = button_data
		self.fg_color = fg_color
		self.bg_color = bg_color
		self._buttons = []
		self._active = False

		# init buttons
		for r in range(self._rows):
			for c in range(self._cols):
				w = int(tft.width()/self._cols)
				h = int(tft.height()/self._rows)-1
				x = c*w
				y = r*h
				bd = self._button_data[(r*self._cols)+c]
				self._buttons.append(button(x,y,w,h,self.fg_color,self.bg_color,bd['label'],bd['callback']))

	def buttons(self):
		return self._buttons

	def getButtonByLabel(self,label):
		for b in self._buttons:
			if b.label==label:
				return b

	def deactivate(self):
		self._active = False

	def render(self):
		global status
		status['screen'] = self._menu_id

		# rows=2
		# cols=3
		# labels=['System On','Button 2','Button 3','System Off','Button 5','Button 6']
		tft.textEnlarge(1)

		for b in self._buttons:
			b.render()
		tft.graphicsMode()
		self._active = True


status = {
	'screen': -1,
	'screenNext': screen.main,
	'touchPoint':{},
	'message': 'startup',
	'enable': 'off' # on/off
}

def handleInterrupt(channel):
	print 'handleInterrupt(' + channel + ')'
	global status
	while tft.touched():
		status['touchPoint'] = tft.touchRead()
		if status['screen'] == screen.main:
			status['screenNext'] = screen.menu
		elif status['screen'] == screen.menu:
			for b in menu_screen.buttons():
				if b.tapped(status['touchPoint']):
					status['message'] = b.label + ' tapped'
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
	tft.textSetCursor(0,100)
	tft.textWrite('System: ' + status['enable'],0)
	tft.graphicsMode()


def enable():
	global status
	status['enable'] = 'on'
	menu_screen.getButtonByLabel('System On').disable()
	menu_screen.getButtonByLabel('System Off').enable()

def disable():
	global status
	status['enable'] = 'off'
	menu_screen.getButtonByLabel('System On').enable()
	menu_screen.getButtonByLabel('System Off').disable()

def test():
	print 'test'


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


menu_screen_buttons = [{
	'label':'System On',
	'callback':enable
	},{
	'label':'Button 2',
	'callback':test
	},{
	'label':'Button 4',
	'callback':test
	},{
	'label':'System Off',
	'callback':disable
	},{
	'label':'Button 5',
	'callback':test
	},{
	'label':'Button 6',
	'callback':test
	}]
menu_screen = menu(screen.menu,2,3,menu_screen_buttons,RA8875_YELLOW,RA8875_RED)

while True:
	try:
		# print 'INT PIN: ' + str(GPIO.input(RA8875_INT))
		# print 'INTC1: ' + hex(tft.readReg(RA8875_INTC1))
		# print 'INTC2: ' + hex(tft.readReg(RA8875_INTC2))
		if GPIO.input(RA8875_INT)==0:
			handleInterrupt(RA8875_INT)
		if status['screen'] != status['screenNext']:
			if status['screenNext'] == screen.main:
				data = {}
				renderMainScreen(data)
			elif status['screenNext'] == screen.menu:
				data = {}
				# renderMenuScreen(data)
				menu_screen.render()

		# sleep(1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()