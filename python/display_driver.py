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
# required args: size, x, y, w, h, fg_color, bg_color
class Control:
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
# required args: size, x, y, w, h, fg_color, bg_color, text
class Label(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)
		self._text = str(kwargs['text'])
		
	def text(self,t=None):
		if t:
			self._text = str(t)
		return self._text

	def render(self):
		tft.textMode()
		tft.textColor(self._fg_color,self._bg_color)
		tft.textSetCursor(self._x,self._y)
		tft.textEnlarge(self._size)
		tft.textWrite(self._text,0)

# required args: size, x, y, w, h, fg_color, bg_color
# options args: datatype, enabled, value
class Input(Control):
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

	def datatype(self):
		return self._datatype

	def enabled(self,en=None):
		if en:
			self._enabled = en
		return self._enabled

	def value(self,val=None):
		if val:
			if self._datatype == t_datatype.text:
				self._value = str(val)
			elif self._datatype == t_datatype.number:
				self._value = int(val)
			else:
				self._value = val
		return self._value

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
		tft.textSetCursor(self._x,self._y)
		tft.textEnlarge(self._size)
		tft.textWrite(self._text,0)


# Button has a tapped event
# required args: size, x, y, w, h, fg_color, bg_color, callback
# options args: datatype, enabled, value, text
class Button(Input):
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

	def callback(self,cb):
		self._callback = cb

	# def render(self):
	# 	if self._enabled:
	# 		bg_color = self._bg_color
	# 	else:
	# 		bg_color = RA8875_BLACK
	# 	tft.graphicsMode()
	# 	tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
	# 	tft.drawRect(self._x,self._y,self._w,self._h,self._fg_color)
	# 	tft.textMode()
	# 	tft.textColor(self._fg_color,bg_color)
	# 	tft.textSetCursor(self._x+10,self._y+int(self._h/2))
	# 	tft.textEnlarge(self._size)
	# 	tft.textWrite(self._text,0)

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

# Spinbox is made up of a Label, an Input, and two Buttons
# Spinbox has a tapped event (passed between both buttons)
# required args: size, x, y, w, h, fg_color, bg_color, callback
# options args: datatype, enabled, value, text, mn, mx
class Spinbox(Input):
	def __init__(self,**kwargs):
		self._callback = callback
		self._min = int(kwargs['mn'])
		self._max = int(kwargs['mx'])
		kwargs['datatype'] = t_datatype.number # spinbox must be number type
		Input.__init__(self,**kwargs)

		self._label = Label(
			size=self._size,
			x=self._x,
			y=self._y,
			w=int(len(self._text)*8*(self._size+1)),
			h=int(16*(self._size+1)),
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			text=self._text
			)

		self._input = Input(
			size=self._size,
			x=self._x+self._label.w(),
			y=self._y,
			w=int(len(self._value)*8*(self._size+1)),
			h=int(16*(self._size+1)),
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			datatype=self._datatype,
			value=self._value
			)

		self._upBtn = Button(
			size=self._size,
			w=8*(self._size+1),
			h=8*(self._size+1),
			x=self._input.x()+self._input.w(),
			y=self._y+(8*(self._size+1)),
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			callback=self.change,
			value=1
			)

		self._dnBtn = Button(
			size=self._size,
			w=8*(self._size+1),
			h=8*(self._size+1),
			x=self._input.x()+self._input.w(),
			y=self._y,
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			callback=self.change,
			value=-1
			)
		
	def change(self,n):
		if self._mn <= self._value+n <= self._mx:
			self._value = self._value+n

	def render(self):
		if self.enabled:
			bg_color = self._bg_color
			self._input.enabled(True)
			self._upBtn.enabled(True)
			self._dnBtn.enabled(True)
		else:
			bg_color = RA8875_BLACK
			self._input.enabled(False)
			self._upBtn.enabled(False)
			self._dnBtn.enabled(False)
		tft.graphicsMode()
		tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		tft.drawRect(self._x,self._y,self._w,self._h,self._fg_color)
		self._label.render()
		self._input.render()
		self._upBtn.render()
		self._dnBtn.render()

	def tapped(self,touchPoint):
		if self._upBtn.tapped(touchPoint):
			return True
		elif self._dnBtn.tapped(touchPoint):
			return True
		return False

# Common class for screens
# required args: id, fg_color, bg_color
# optional args: controls
class Screen:
	def __init__(self,**kwargs):
		self._id = kwargs['id']
		self._fg_color = kwargs['fg_color']
		self._bg_color = kwargs['bg_color']
		self._active = False

		if 'controls' in kwargs:
			self._controls = kwargs['controls']
		else:
			self._controls = []

	def controls(self):
		return self._controls

	def deactivate(self):
		self._active = False

	def activate(self):
		global status
		status['screen'] = self._id
		tft.graphicsMode()
		tft.fillScreen(self._bg_color)

		for c in self._controls:
			c.render()
		tft.graphicsMode()
		self._active = True

# required args: id, fg_color, bg_color, rows, cols, button_data
class ButtonGrid(Screen):
	def __init__(self,**kwargs):
		self._rows = rows
		self._cols = cols
		kwargs['controls'] = []

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
					callback = None
					)
				kwargs['controls'].append(btn)

		Screen.__init__(self,**kwargs)


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
			for c in menu_screen.controls():
				if c.tapped(status['touchPoint']):
					status['message'] = c.text() + ' tapped'
			status['screenNext'] = t_screen.main

# def renderMainScreen(data):
# 	print 'renderMainScreen(' + str(data) + ')'
# 	global status
# 	status['screen'] = t_screen.main
# 	tft.fillScreen(RA8875_BLUE)
# 	# may need to monitor wait signal in textMode
# 	tft.textMode()
# 	tft.textEnlarge(3)
# 	tft.textColor(RA8875_WHITE,RA8875_BLUE)
# 	tft.textSetCursor(0,0)
# 	tft.textWrite(status['message'],0)
# 	tft.textSetCursor(0,100)
# 	tft.textWrite('System: ' + status['enable'],0)
# 	tft.graphicsMode()

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
tft.touchEnable(True)

GPIO.setup(RA8875_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

main_screen = Screen(
		id=t_screen.main,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLUE
		)

lbl = Label(
		size=2,
		x=50,
		y=240,
		w=700,
		h=120,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_MAGENTA,
		text='Testing...'
		)

main_screen.controls().append(lbl)

menu_screen = ButtonGrid(
		id=t_screen.menu,
		rows=2,
		cols=3,
		fg_color=RA8875_YELLOW,
		bg_color=RA8875_RED
		)

menu_screen.controls[0].text('Button 1')
menu_screen.controls[0].callback(test)
menu_screen.controls[0].value(True)



while True:
	try:
		# print 'INT PIN: ' + str(GPIO.input(RA8875_INT))
		# print 'INTC1: ' + hex(tft.readReg(RA8875_INTC1))
		# print 'INTC2: ' + hex(tft.readReg(RA8875_INTC2))
		if GPIO.input(RA8875_INT)==0:
			handleInterrupt(RA8875_INT)
		if status['screen'] != status['screenNext']:
			if status['screenNext'] == t_screen.main:
				main_screen.activate()
			elif status['screenNext'] == t_screen.menu:
				menu_screen.activate()

		# sleep(1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()