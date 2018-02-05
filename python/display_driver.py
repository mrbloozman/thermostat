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
	spin = 2
	toggle = 3
	listbx = 4

class t_datatype(enum.Enum):
	text = 0
	number = 1
	boolean = 2
	submit = 3

# common class for all controls
# border, padding?
# required args: size, x, y, fg_color, bg_color
# optional args: w, h
class Control:
	def __init__(self,**kwargs):
		if 'size' in kwargs:
			self._size = int(kwargs['size']) # text enlargement size 0-3
		else:
			self._size = 0

		if 'fg_color' in kwargs:
			self._fg_color = kwargs['fg_color']
		else:
			self._fg_color = RA8875_WHITE

		if 'bg_color' in kwargs:
			self._bg_color = kwargs['bg_color']
		else:
			self._bg_color = RA8875_BLACK

		if 'text' in kwargs:
			self._text = str(kwargs['text'])
		else:
			self._text = ''

		if 'x' in kwargs:
			self._x = int(kwargs['x'])
		else:
			self._x = 0

		if 'y' in kwargs:
			self._y = int(kwargs['y'])
		else:
			self._y = 0

		if 'w' in kwargs:
			self._w = int(kwargs['w'])
		else:
			self._w = self.text_width()

		if 'h' in kwargs:
			self._h = int(kwargs['h'])
		else:
			self._h = self.text_height()

		if 'border' in kwargs:
			self._border = int(kwargs['border'])
		else:
			self._border = 1

	def text(self,t=None):
		if t:
			self._text = str(t)
		return self._text

	def border(self,b=None):
		if b:
			self._border = int(b)
		return self._border

	def text_width(self):
		return 8*len(self._text)*(1+self._size)

	def text_height(self):
		return 16*(1+self._size)

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

	def left(self,x=None):
		if x:
			x = int(x)
		else:
			x = 0
		self._x = x

	def center(self,x=None):
		if x:
			x = int(x)
		else:
			x = int(tft.width()/2)
		self._x = x-int(self._w/2)

	def right(self,x=None):
		if x:
			x = int(x)
		else:
			x = tft.width()
		self._x = x-self._w

	def top(self,y=None):
		if y:
			y = int(y)
		else:
			y = 0
		self._y = y

	def middle(self,y=None):
		if y:
			y = int(y)
		else:
			y = int(tft.height()/2)
		self._y = y-int(self._h/2)

	def bottom(self,y=None):
		if y:
			y = int(y)
		else:
			y = tft.height()
		self._y = y-self._h

	def tapped(self,tp):
		return False	# default response

	def render(self):
		tft.graphicsMode()
		tft.fillRect(self._x,self._y,self._w,self._h,self.bg_color())
		for b in range(self._border):
			tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self.fg_color())
		tft.textMode()
		tft.textColor(self.fg_color(),self.bg_color())
		# setting for center/middle of rect
		tft.textSetCursor(self._x+int(self._w/2)-int(self.text_width()/2),self._y+int(self._h/2)-int(self.text_height()/2))
		tft.textEnlarge(self._size)
		tft.textWrite(self._text,0)
		tft.graphicsMode()

# do I need multi-line labels?
# required args: size, x, y, w, h, fg_color, bg_color, text
class Label(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)

# required args: size, fg_color, bg_color, rows, cols
class Grid(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)
		self._rows=int(kwargs['rows'])
		self._cols=int(kwargs['cols'])

		if 'controls' in kwargs:
			self._controls = kwargs['controls']
		else:
			self._controls = []

		self.position()

	def position(self):
		for r in range(self._rows):
			for c in range(self._cols):
				i = c+(r*self._cols)
				self._controls[i].x(self._x+int(c*self._w/self._cols))
				self._controls[i].y(self._y+int(r*self._h/self._rows))
				self._controls[i].w(int(self._w/self._cols))
				self._controls[i].h(int(self._h/self._rows))

	def left(self,x=None):
		Control.left(self,x)
		self.position()

	def center(self,x=None):
		Control.center(self,x)
		self.position()

	def right(self,x=None):
		Control.right(self,x)
		self.position()

	def top(self,y=None):
		Control.top(self,y)
		self.position()

	def middle(self,y=None):
		Control.middle(self,y)
		self.position()

	def bottom(self,y=None):
		Control.bottom(self,y)
		self.position()

	def controls(self,cs=None):
		if cs:
			self._controls = cs
		return self._controls

	def render(self):
		Control.render(self)
		for c in self._controls:
			c.render()

	def tapped(self,touchPoint):
		for c in self._controls:
			if c.tapped(touchPoint):
				return True
		return False
	

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
			self._value = 0
		else:
			self._value = False

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
		elif val==0:
			self._value = val
		return self._value

	def value_width(self):
		return 8*len(str(self._value))*(1+self._size)

	def value_height(self):
		return 16*(1+self._size)

	def change(self,val):
		if self._value != val:
			if self._datatype == t_datatype.text:
				self._value = str(val)
			elif self._datatype == t_datatype.number:
				self._value = int(val)
			else:
				self._value = val
			self.render()

	def render(self):
		if self._enabled:
			bg_color = self._bg_color
		else:
			bg_color = RA8875_BLACK
		tft.graphicsMode()
		tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		for b in range(self._border):
			tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self._fg_color)
		tft.textMode()
		tft.textColor(self._fg_color,bg_color)
		# setting for center/middle of rect
		tft.textSetCursor(self._x+int(self._w/2)-int(self.value_width()/2),self._y+int(self._h/2)-int(self.value_height()/2))
		tft.textEnlarge(self._size)
		tft.textWrite(str(self._value),0)
		tft.graphicsMode()


# Button has a tapped event
# required args: size, x, y, w, h, fg_color, bg_color
# options args: datatype, enabled, value, text, callback
class Button(Input):
	def __init__(self,**kwargs):
		Input.__init__(self,**kwargs)

		if 'callback' in kwargs:
			self._callback = kwargs['callback']
		else:
			self._callback = self.skip

	def skip(self,x):
		pass

	def callback(self,cb):
		self._callback = cb

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

	def render(self):
		Control.render(self)

class Toggle(Button):
	def __init__(self,**kwargs):
		Button.__init__(self,**kwargs)

		if 'selected' in kwargs:
			self._selected = bool(selected)
		else:
			self._selected = False

	def selected(self,s=None):
		if s:
			self._selected = bool(s)
		elif s==False:
			self._selected = s
		return self._selected

	def fg_color(self,fg_color=None):
		if fg_color:
			self._fg_color = int(fg_color)
		if self._selected:
			return self._fg_color
		else:
			return self._bg_color

	def bg_color(self,bg_color=None):
		if bg_color:
			self._bg_color = int(bg_color)
		if self._selected:
			return self._bg_color
		else:
			return self._fg_color

	def tapped(self,touchPoint):
		if Button.tapped(self,touchPoint):
			self._selected = ~self._selected
			self.render()





# Spinbox is made up of a Label, an Input, and two Buttons
# Spinbox has a tapped event (passed between both buttons)
# required args: size, x, y, w, h, fg_color, bg_color
# options args: datatype, enabled, value, text, mn, mx, callback
class Spinbox(Input):
	def __init__(self,**kwargs):
		kwargs['datatype'] = t_datatype.number # spinbox must be number type
		Input.__init__(self,**kwargs)

		if 'mn' in kwargs:
			self._mn = int(kwargs['mn'])
		else:
			self._mn = -99

		if 'mx' in kwargs:
			self._mx = int(kwargs['mx'])
		else: 
			self._mx = 100

		if 'callback' in kwargs:
			self._callback = kwargs['callback']
		else:
			self._callback = self.skip

		self._label = Label(
			border=0,
			size=self._size,
			x=0,
			y=0,
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			text=self._text
			)

		if len(str(self._mn)) > len(str(self._mx)):
			maxlen = len(str(self._mn))+1
		else:
			maxlen = len(str(self._mx))+1

		self._input = Input(
			border=0,
			size=self._size,
			x=0,
			y=0,
			w=8*maxlen*(self._size+1),
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			datatype=self._datatype,
			value=self._value
			)

		self._upBtn = Button(
			border=0,
			size=self._size,
			x=0,
			y=0,
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			callback=self.change,
			value=1,
			text=chr(0x1e)
			)

		self._dnBtn = Button(
			border=0,
			size=self._size,
			x=0,
			y=0,
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			callback=self.change,
			value=-1,
			text=chr(0x1f)
			)

		self.position()

		if 'w' not in kwargs:
			self._w = self._label.w()+self._input.w()+self._upBtn.w()

		if 'h' not in kwargs:
			self._h = self._upBtn.h()+self._dnBtn.h()

	def position(self):
		self._label.x(self._x+int(self._w/2)-self._label.w())
		self._label.y(self._y+int(self._h/2)-int(self._label.h()/2))
		self._input.x(self._x+int(self._w/2))
		self._input.y(self._y+int(self._h/2)-int(self._input.h()/2))
		self._upBtn.x(self._input.x()+self._input.w())
		self._upBtn.y(self._input.y()-int(self._upBtn.h()/2))
		self._dnBtn.x(self._input.x()+self._input.w())
		self._dnBtn.y(self._input.y()+int(self._upBtn.h()/2))

	def left(self,x=None):
		Input.left(self,x)
		self.position()

	def center(self,x=None):
		Input.center(self,x)
		self.position()

	def right(self,x=None):
		Input.right(self,x)
		self.position()

	def top(self,y=None):
		Input.top(self,y)
		self.position()

	def middle(self,y=None):
		Input.middle(self,y)
		self.position()

	def bottom(self,y=None):
		Input.bottom(self,y)
		self.position()

	def skip(self,x):
		pass

	def callback(self,cb):
		self._callback = cb
		
	def change(self,n):
		# print 'change('+str(n)+')'
		if self._mn <= self._value+n <= self._mx:
			self._value = self._value+n
			self._input.value(self._value)
			self._input.render()

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
		# print 'spinbox tapped()'
		if self._upBtn.tapped(touchPoint):
			self._callback(self._value)
			return True
		elif self._dnBtn.tapped(touchPoint):
			self._callback(self._value)
			return True
		return False

# Listbox is a container for Toggle instances - toggles callbacks will be overwritten to control the listbox value
class Listbox(Grid,Input):
	def __init__(self,**kwargs):
		kwargs['cols']=1
		if 'controls' in kwargs:
			kwargs['rows']=len(kwargs['controls'])
		else:
			kwargs['rows']=0

		Grid.__init__(self,**kwargs)
		Input.__init__(self,**kwargs)

		for t in self._controls:
			t.callback(self.change)
		self.change(self._value)

	def change(self,val):
		for t in self._controls:
			if val == t.value():
				t.selected(True)
			else:
				t.selected(False)


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

	def id(self):
		return self._id

	def fg_color(self,fg=None):
		if fg:
			self._fg_color = fg
		return self._fg_color

	def bg_color(self,bg=None):
		if bg:
			self._bg_color = bg
		return self._bg_color

	def controls(self,controls=None):
		if controls:
			self._controls=controls
		return self._controls

	def active(self,x=None):
		global status
		global screens
		if x:
			status['screen'] = self._id
			for s in screens:
				s.active(False)
			tft.graphicsMode()
			tft.fillScreen(self._bg_color)

			for c in self._controls:
				c.render()
			tft.graphicsMode()
			self._active = True
		else:
			self._active = False



		


status = {
	'screen': -1,
	'touchPoint':{},
	'message': 'startup',
	'enable': 'off' # on/off
}

def getScreen(id):
	global screens
	for s in screens:
		if s.id() == id:
			return s
	return False

def handleInterrupt(channel):
	# print 'handleInterrupt(' + channel + ')'
	global status
	while tft.touched():
		status['touchPoint'] = tft.touchRead()
	s = getScreen(status['screen'])
	for c in s.controls():
		if c.tapped(status['touchPoint']):
			status['message'] = c.text() + ' tapped'
			# print status['message']



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

###############	screens ###############
main_screen = Screen(
		id=t_screen.main,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLUE
		)

menu_screen = Screen(
		id=t_screen.menu,
		fg_color=RA8875_YELLOW,
		bg_color=RA8875_RED
		)

spin_screen = Screen(
		id=t_screen.spin,
		fg_color=RA8875_YELLOW,
		bg_color=RA8875_BLACK
		)

toggle_screen = Screen(
		id=t_screen.toggle,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLUE
		)

listbox_screen = Screen(
		id=t_screen.listbx,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_RED
		)

screens = [main_screen,menu_screen,spin_screen,toggle_screen,listbox_screen]

###############	main_screen controls ###############
lbl = Label(
		size=2,
		x=50,
		y=240,
		w=700,
		h=120,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_MAGENTA,
		text=status['message']
		)
lbl.center()

# required args: size, x, y, w, h, fg_color, bg_color
# options args: datatype, enabled, value, text, callback
menu_btn = Button(
		size=1,
		x=0,
		y=0,
		w=100,
		h=75,
		fg_color=RA8875_BLACK,
		bg_color=RA8875_WHITE,
		callback=menu_screen.active,
		value=True,
		text='MENU'
		)
menu_btn.center()
menu_btn.border(10)

main_screen.controls().append(lbl)
main_screen.controls().append(menu_btn)

###############	menu_screen controls ###############
mainscreen_btn = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		value=True,
		callback=main_screen.active,
		text='Main Screen'
		)

spinscreen_btn = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		value=True,
		callback=spin_screen.active,
		text='Spinbox Test'
		)

test_btn1 = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		text='Toggle Test',
		callback=toggle_screen.active,
		value=True
		)

test_btn2 = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		text='Test 1'
		)

menu_grid = Grid(
		border=5,
		size=1,
		w=600,
		h=380,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		rows=2,
		cols=2,
		controls=[mainscreen_btn,spinscreen_btn,test_btn1,test_btn2]
		)

menu_grid.center()
menu_grid.middle()

menu_screen.controls().append(menu_grid)

###############	spin_screen controls ###############
# required args: size, x, y, w, h, fg_color, bg_color
# options args: datatype, enabled, value, text, mn, mx, callback
sbox = Spinbox(
		size=3,
		w=500,
		h=250,
		fg_color=spin_screen.fg_color(),
		bg_color=spin_screen.bg_color(),
		value=10,
		text='Spin: ',
		mn=0,
		mx=20
	)
sbox.center()
sbox.middle()

submit_btn = Button(
		size=2,
		fg_color=RA8875_BLACK,
		bg_color=RA8875_YELLOW,
		callback=main_screen.active,
		value=True,
		text='SUBMIT'
		)
submit_btn.center()
submit_btn.bottom(400)

spin_screen.controls().append(sbox)
spin_screen.controls().append(submit_btn)

###############	toggle_screen controls ###############
fg = toggle_screen.fg_color()
bg = toggle_screen.bg_color()

display_input = Input(
		size=2,
		fg_color=fg,
		bg_color=bg,
		datatype=t_datatype.text,
		value='Tap...'
		)

t1 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Toggle 1',
		datatype=t_datatype.text,
		value='Got 1!',
		callback=display_input.change
		)

t2 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Toggle 2',
		datatype=t_datatype.text,
		value='Got 2!',
		callback=display_input.change
		)

t3 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Toggle 3',
		datatype=t_datatype.text,
		value='Got 3!',
		callback=display_input.change
		)

display_input.center()
display_input.top()

tgrid = Grid(
		fg_color=fg,
		bg_color=bg,
		rows=1,
		cols=3,
		controls=[t1,t2,t3],
		w=700,
		h=300
		)

tgrid.center()
tgrid.middle()

toggle_screen.controls([display_input,tgrid])

###############	listbx_screen controls ###############
fg = toggle_screen.fg_color()
bg = toggle_screen.bg_color()

lbl= Label(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Select...'
		)

t1 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Item 1',
		datatype=t_datatype.text,
		value='Got 1!'
		)

t2 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Item 2',
		datatype=t_datatype.text,
		value='Got 2!'
		)

t3 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Item 3',
		datatype=t_datatype.text,
		value='Got 3!',
		)

lbl.center(150)
lbl.middle()

lbox = Listbox(
		fg_color=fg,
		bg_color=bg,
		controls=[t1,t2,t3],
		w=500,
		h=400
		)

lbox.center(550)
lbox.middle()

btn = Button(
		border=2,
		size=3,
		w=25,
		h=25,
		fg_color=fg,
		bg_color=bg,
		text='OK',
		callback=main_screen.active
		value=True
		)

btn.center(150)
btn.middle(350)

listbox_screen.controls([lbl,lbox])




####################################################



main_screen.active(True)

while True:
	try:
		if GPIO.input(RA8875_INT)==0:
			handleInterrupt(RA8875_INT)

	except KeyboardInterrupt:
		GPIO.cleanup()
		raise
GPIO.cleanup()