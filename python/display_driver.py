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

class t_screen(enum.Enum):
	main = 0
	menu = 1

class t_datatype(enum.Enum):
	text = 0
	number = 1
	boolean = 2
	submit = 3

# do I need multi-line labels?
class Label:
	def __init__(self,text,size):
		self._text = str(text)
		self._size = int(size) # text enlargement size 0-3
		
	def text(self,t=None):
		if t:
			self._text = str(t)
		return self._text

	def size(self,s=None):
		if s:
			self._size = int(s)
		return self._size

	# assuming 1x cursor size is 8x16 pixels
	def width(self):
		return len(text)*8*(self._size+1)

	def height(self):
		return 16*(self._size+1) # assuming single line


class Input:
	def __init__(self,x,y,w,h,fg_color,bg_color,label,datatype):
		self.x = int(x)
		self.y = int(y)
		self.w = int(w)
		self.h = int(h)
		self.fg_color = fg_color
		self.bg_color = bg_color
		self.label = label
		self.enabled = True
		self._datatype = datatype

		if self._datatype == t_datatype.text:
			self.value = ''
		elif self._datatype == t_datatype.number:
			self.value = 0
		else:
			self.value = False

# Spinbox has a tapped event (passed between both buttons)
class Spinbox:
	def __init__(self,x,y,fg_color,bg_color,label,mn,mx,callback):
		self._callback = callback
		self._min = int(mn)
		self._max = int(mx)
		btnw = (label.size()*16)
		btnh = (label.size()*32)
		w = label.width() + btnw
		h = label.height() + btnh
		Input.__init__(self,x,y,w,h,fg_color,bg_color,label,t_datatype.number)

		btnx = self._x+self.label.width()
		self._upBtn = Button(btnx,self._y+btnh,btnw,btnh,fg_color,bg_color,Label('up',0),self.increase)
		self._dnBtn = Button(btnx,self._y,btnw,btnh,fg_color,bg_color,Label('dn',0),self.decrease)

	def render(self):
		if self.enabled:
			bg_color = self.bg_color
			self._upBtn.enabled = True
			self._dnBtn.enabled = True
		else:
			bg_color = RA8875_BLACK
			self._upBtn.enabled = False
			self._dnBtn.enabled = False
		tft.graphicsMode()
		tft.fillRect(self.x,self.y,self.w,self.h,bg_color)
		tft.drawRect(self.x,self.y,self.w,self.h,self.fg_color)
		tft.textMode()
		tft.textColor(self.fg_color,bg_color)
		tft.textSetCursor(self.x,self.y+int(self.h/2))
		tft.textEnlarge(self.label.size())
		tft.textWrite(self.label.text(),0)
		self._upBtn.render()
		self._dnBtn.render()

	def increase(self):
		if self.value < self._max:
			self.value = self.value + 1

	def decrease(self):
		if self.value > self._min:
			self.value = self.value - 1

	def tapped(self,touchPoint):
		if self._upBtn.tapped(touchPoint):
			return True
		elif self._dnBtn.tapped(touchPoint):
			return True
		return False

# Button has a tapped event
class Button:
	def __init__(self,x,y,w,h,fg_color,bg_color,label,callback):
		Input.__init__(self,x,y,w,h,fg_color,bg_color,label,t_datatype.boolean)
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
		tft.textEnlarge(self.label.size())
		tft.textWrite(self.label.text(),0)

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
				self._buttons.append(Button(x,y,w,h,self.fg_color,self.bg_color,bd['label'],bd['callback']))

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
		# tft.textEnlarge(1)

		for b in self._buttons:
			b.render()
		tft.graphicsMode()
		self._active = True


status = {
	'screen': -1,
	'screenNext': t_screen.main,
	'touchPoint':{},
	'message': 'startup',
	'enable': 'off' # on/off
}

def handleInterrupt(channel):
	print 'handleInterrupt(' + channel + ')'
	global status
	while tft.touched():
		status['touchPoint'] = tft.touchRead()
		if status['screen'] == t_screen.main:
			status['screenNext'] = t_screen.menu
		elif status['screen'] == t_screen.menu:
			for b in menu_screen.buttons():
				if b.tapped(status['touchPoint']):
					status['message'] = b.label + ' tapped'
			status['screenNext'] = t_screen.main

def renderMainScreen(data):
	print 'renderMainScreen(' + str(data) + ')'
	global status
	status['screen'] = t_screen.main
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
	'label': Label('System On',1),
	'callback':enable
	},{
	'label':Label('Button 2',1),
	'callback':test
	},{
	'label':Label('Button 4',1),
	'callback':test
	},{
	'label':Label('System Off',1),
	'callback':disable
	},{
	'label':Label('Button 5',1),
	'callback':test
	},{
	'label':Label('Button 6',1),
	'callback':test
	}]
menu_screen = menu(t_screen.menu,2,3,menu_screen_buttons,RA8875_YELLOW,RA8875_RED)

while True:
	try:
		# print 'INT PIN: ' + str(GPIO.input(RA8875_INT))
		# print 'INTC1: ' + hex(tft.readReg(RA8875_INTC1))
		# print 'INTC2: ' + hex(tft.readReg(RA8875_INTC2))
		if GPIO.input(RA8875_INT)==0:
			handleInterrupt(RA8875_INT)
		if status['screen'] != status['screenNext']:
			if status['screenNext'] == t_screen.main:
				data = {}
				renderMainScreen(data)
			elif status['screenNext'] == t_screen.menu:
				data = {}
				# renderMenuScreen(data)
				menu_screen.render()

		# sleep(1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()