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

# common class for all controls
# border, padding?
class Control:
	# required args: size, x, y, w, h, fg_color, bg_color
	def __init__(self,**kwargs):
		self._size = int(kwargs['size']) # text enlargement size 0-3
		self._x = int(kwargs['x'])
		self._y = int(kwargs['y'])
		self._w = int(kwargs['w'])
		self._h = int(kwargs['h'])
		self._fg_color = kwargs['fg_color']
		self._bg_color = kwargs['bg_color']

	def size(self,s=None):
		if s:
			self._size = int(s)
		return self._size

	def x(self,x=None):
		if x:
			self._x = int(x)
		return self._x

	def y(self,y=None):
		if y:
			self._y = int(y)
		return self._y

	def w(self,w=None):
		if w:
			self._w = int(w)
		return self._w

	def h(self,h=None):
		if h:
			self._h = int(h)
		return self._h

	def fg_color(self,fg_color=None):
		if fg_color:
			self._fg_color = int(fg_color)
		return self._fg_color

	def bg_color(self,bg_color=None):
		if bg_color:
			self._bg_color = int(bg_color)
		return self._bg_color

# do I need multi-line labels?
class Label(Control):
	# required args: size, x, y, w, h, fg_color, bg_color, text
	def __init__(self,**kwargs):
		kwargs['w']=0
		kwargs['h']=0
		Control.__init__(self,**kwargs)
		self._text = str(kwargs['text'])
		self.w(self.width())
		self.h(self.height())
		
	def text(self,t=None):
		if t:
			self._text = str(t)
		return self._text

	# assuming 1x cursor size is 8x16 pixels
	def width(self):
		return len(text)*8*(self._size+1)

	def height(self):
		return 16*(self._size+1) # assuming single line

	def render(self):
		tft.textMode()
		tft.textColor(self._fg_color,self._bg_color)
		tft.textSetCursor(self._x,self._y)
		tft.textEnlarge(self._size)
		tft.textWrite(self._text,0)

class Input(Control):
	# required args: size, x, y, w, h, fg_color, bg_color
	# options args: datatype, enabled, value
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)

		if 'datatype' in kwargs:
			self._datatype = kwargs['datatype']
		else:
			self._datatype = t_datatype.boolean

		if 'enabled' in kwargs:
			self._enabled = kwargs['enabled']
		else:
			self._enabled = True

		if 'value' in kwargs:
			self._value = kwargs['value']
		elif self._datatype == t_datatype.text:
			self.value = ''
		elif self._datatype == t_datatype.number:
			self.value = 0
		else:
			self.value = False

# Button has a tapped event
class Button(Input):
	# required args: size, x, y, w, h, fg_color, bg_color, callback
	# options args: datatype, enabled, value, text
	def __init__(self,**kwargs):
		Input.__init__(self,**kwargs)
		self._callback = kwargs['callback']

		if 'text' in kwargs:
			self._text = str(kwargs['text'])
		else:
			self._text = ''

	def text(self,t=None):
		if t:
			self._text = str(t)
		return self._text

	def render(self):
		if self._enabled:
			bg_color = self._bg_color
		else:
			bg_color = RA8875_BLACK
		tft.graphicsMode()
		tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		tft.drawRect(self._x,self._y,self._w,self._h,self._fg_color)
		tft.textMode()
		tft.textColor(self._fg_color,bg_color)
		tft.textSetCursor(self._x+10,self._y+int(self._h/2))
		tft.textEnlarge(self._size)
		tft.textWrite(self._text,0)

	def tapped(self,touchPoint):
		if not self._enabled:
			return False
		tp = touchPoint
		nw = self._w * 1024 / tft.width()	# normalized button width
		nh = self._h * 1024 / tft.height()	# normalized button height
		nx = self._x * 1024 / tft.width()	# normalized button x position
		ny = self._y * 1024 / tft.height()	# normalized button y position
		if nx <= tp['x'] <= (nx+nw):
			if ny <= tp['y'] <= (ny+nh):
				self._callback(self._value)
				return True
			else:
				return False
		else:
			return False

# Spinbox has a tapped event (passed between both buttons)
class Spinbox(Input):
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



class menu:
	def __init__(self,menu_id,rows,cols,button_data,fg_color,bg_color):
		self._menu_id = menu_id
		self._rows = rows
		self._cols = cols
		self._button_data = button_data
		self._fg_color = fg_color
		self._bg_color = bg_color
		self._buttons = []
		self._active = False

		# init buttons
		# required args: size, x, y, w, h, fg_color, bg_color, callback
		# options args: datatype, enabled, value
		for r in range(self._rows):
			for c in range(self._cols):
				bd = self._button_data[(r*self._cols)+c]
				w = int(tft.width()/self._cols)
				h = int(tft.height()/self._rows)-1
				btn = Button(size=1,
					w = w,
					h = h,
					x = c*w,
					y = r*h,
					fg_color = self._fg_color,
					bg_color = self._bg_color,
					callback = bd['callback'],
					text = bd['label'],
					value = bd['value'])
				self._buttons.append(btn)

	def buttons(self):
		return self._buttons

	# def getButtonByLabel(self,label):
	# 	for b in self._buttons:
	# 		if b.label==label:
	# 			return b

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
					status['message'] = b.text() + ' tapped'
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


def enable(x):
	global status
	status['enable'] = 'on'
	menu_screen.buttons()[0].enabled=False
	menu_screen.buttons()[3].enabled=True

def disable(x):
	global status
	status['enable'] = 'off'
	menu_screen.buttons()[0].enabled=True
	menu_screen.buttons()[3].enabled=False

def test(x):
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
	'label': 'System On',
	'callback':enable,
	'value':True
	},{
	'label':'Button 2',
	'callback':test,
	'value':0
	},{
	'label':'Button 4',
	'callback':test,
	'value':0
	},{
	'label':'System Off',
	'callback':disable,
	'value':False
	},{
	'label':'Button 5',
	'callback':test,
	'value':0
	},{
	'label':'Button 6',
	'callback':test,
	'value':0
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