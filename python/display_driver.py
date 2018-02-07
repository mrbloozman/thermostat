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
# padding?
class Control:
	def __init__(self,**kwargs):
		if 'onTap' in kwargs:
			self._onTap = kwargs['onTap']
		else:
			self._onTap = self.skip

		if 'onTapArgs' in kwargs:
			self._onTapArgs = kwargs['onTapArgs']
		else:
			self._onTapArgs = []

		if 'onRender' in kwargs:
			self._onRender = kwargs['onRender']
		else:
			self._onRender = self.skip

		if 'onRenderArgs' in kwargs:
			self._onRenderArgs = kwargs['onRenderArgs']
		else:
			self._onRenderArgs = []

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

	def skip(self,*args):
		pass

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

	def listArgs(self,*args):
		arglist = []
		for a in args:
			try:
				arglist.append(getattr(self,a))
			except:
				arglist.append(a)
		return arglist

	def tapped(self,touchPoint):
		tp = touchPoint
		nw = self._w * 1024 / tft.width()	# normalized width
		nh = self._h * 1024 / tft.height()	# normalized height
		nx = self._x * 1024 / tft.width()	# normalized x position
		ny = self._y * 1024 / tft.height()	# normalized y position
		if nx <= tp['x'] <= (nx+nw):
			if ny <= tp['y'] <= (ny+nh):
				# print self.listArgs(*self._onTapArgs)
				self._onTap(*self.listArgs(*self._onTapArgs))
				return True
			else:
				return False
		else:
			return False

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
		self._onRender(*self.listArgs(*self._onRenderArgs))


# do I need multi-line labels?
class Label(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)

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
			c.tapped(touchPoint)
		if Control.tapped(self,touchPoint):
			return True
		else:
			return False
	
class Input(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)

		if 'onChange' in kwargs:
			self._onChange = kwargs['onChange']
		else:
			self._onChange = self.skip

		if 'onChangeArgs' in kwargs:
			self._onChangeArgs = kwargs['onChangeArgs']
		else:
			self._onChangeArgs = []

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
			self.render()
		elif en==False:
			self._enabled = en
			self.render()
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
			self.value(val)
			self._onChange(*self.listArgs(*self._onChangeArgs))
			self.render()

	def tapped(self,touchPoint):
		if not self._enabled:
			return False
		else:
			return Control.tapped(self,touchPoint)

	def render(self):
		if self._enabled:
			bg_color = self.bg_color()
		else:
			bg_color = RA8875_BLACK		# probably will need a more clear disabled style i.e. gray, italic, strikethrough, etc
		tft.graphicsMode()
		tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		for b in range(self._border):
			tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self.fg_color())
		tft.textMode()
		tft.textColor(self.fg_color(),bg_color)
		# setting for center/middle of rect
		tft.textSetCursor(self._x+int(self._w/2)-int(self.value_width()/2),self._y+int(self._h/2)-int(self.value_height()/2))
		tft.textEnlarge(self._size)
		tft.textWrite(str(self._value),0)
		tft.graphicsMode()
		self._onRender(*self.listArgs(*self._onRenderArgs))

class Button(Input):
	def __init__(self,**kwargs):
		Input.__init__(self,**kwargs)
		self._datatype = t_datatype.text
		self._value = self._text	# button's value is its text

class Toggle(Button):
	def __init__(self,**kwargs):
		Button.__init__(self,**kwargs)

		if 'selected' in kwargs:
			self._selected = bool(kwargs['selected'])
		else:
			self._selected = False

		if 'onSelect' in kwargs:
			self._onSelect = kwargs['onSelect']
		else:
			self._onSelect = self.skip

		if 'onSelectArgs' in kwargs:
			self._onSelectArgs = kwargs['onSelectArgs']
		else:
			self._onSelectArgs = []

	def selected(self,s=None):
		if s:
			self._selected = bool(s)
			self._onSelect(*self.listArgs(*self._onSelectArgs))
			self.render()
		elif s==False:
			self._selected = s
			self._onSelect(*self.listArgs(*self._onSelectArgs))
			self.render()
		return self._selected

	def fg_color(self,fg_color=None):
		if fg_color:
			self._fg_color = int(fg_color)
		if not self._selected:
			return self._fg_color
		else:
			return self._bg_color

	def bg_color(self,bg_color=None):
		if bg_color:
			self._bg_color = int(bg_color)
		if not self._selected:
			return self._bg_color
		else:
			return self._fg_color

	def tapped(self,touchPoint):
		if Button.tapped(self,touchPoint):
			self.selected(not self._selected)

# Spinbox is made up of a Label, an Input, and two Buttons
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

		self._label = Label(
			border=0,
			size=self._size,
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
			w=8*maxlen*(self._size+1),
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			datatype=self._datatype,
			value=self._value
			)

		self._upBtn = Button(
			border=0,
			size=self._size,
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			onTap=self.change,
			onTapArgs=[1],
			text=chr(0x1e)
			)

		self._dnBtn = Button(
			border=0,
			size=self._size,
			fg_color=self._fg_color,
			bg_color=self._bg_color,
			onTap=self.change,
			onTapArgs=[-1],
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
		
	def change(self,n):
		val = self._value+n
		if self._mn <= val <= self._mx:
			Input.change(self,val)
			self._input.change(self._value)

	def enabled(self,en=None):
		if en:
			self._input.enabled(en)
			self._upBtn.enabled(en)
			self._dnBtn.enabled(en)
		return Input.enabled(self,en)


	def render(self):
		if self._enabled:
			bg_color = self._bg_color
		else:
			bg_color = RA8875_BLACK
		tft.graphicsMode()
		tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		tft.drawRect(self._x,self._y,self._w,self._h,self._fg_color)
		self._label.render()
		self._input.render()
		self._upBtn.render()
		self._dnBtn.render()

	def tapped(self,touchPoint):
		self._upBtn.tapped(touchPoint)
		self._dnBtn.tapped(touchPoint)
		return Input.tapped(self,touchPoint)

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
			t._onTap = self.change
			t._onTapArgs = [t._value]
		self.value(self._value)

	def value(self,val=None):
		if val:
			for t in self._controls:
				if val != t.value():
					t._selected=False
		return Input.value(self,val)

	def enabled(self,en=None):
		if en or en==False:
			for c in self.controls():
				c.enabled(en)
		return Input.enabled(self,en)


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
		size=3,
		w=200,
		h=150,
		y=20,
		fg_color=RA8875_BLACK,
		bg_color=RA8875_WHITE,
		onTap=menu_screen.active,
		onTapArgs=[True],
		text='MENU'
		)
menu_btn.center()
menu_btn.border(7)

main_screen.controls().append(lbl)
main_screen.controls().append(menu_btn)

###############	menu_screen controls ###############
mainscreen_btn = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		onTapArgs=[True],
		onTap=main_screen.active,
		text='Main Screen'
		)

spinscreen_btn = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		onTapArgs=[True],
		onTap=spin_screen.active,
		text='Spinbox Test'
		)

test_btn1 = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		text='Toggle Test',
		onTap=toggle_screen.active,
		onTapArgs=[True]
		)

test_btn2 = Button(
		border=5,
		size=1,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		text='Listbox Test',
		onTap=listbox_screen.active,
		onTapArgs=[True]
		)

lbl0 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl0'
	)

lbl1 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl1'
	)

lbl2 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl2'
	)

lbl3 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl3'
	)

lbl4 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl4'
	)

lbl5 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl5'
	)

lbl6 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl6'
	)

lbl7 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl7'
	)

lbl8 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl8'
	)

lbl9 = Label(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_BLUE,
		text='lbl9'
	)

mini_grid = Grid(
		border=5,
		fg_color=RA8875_CYAN,
		bg_color=RA8875_MAGENTA,
		rows=3,
		cols=3,
		controls=[lbl1,lbl2,lbl3,lbl4,lbl5,lbl6,lbl7,lbl8,lbl9])

menu_grid = Grid(
		border=5,
		size=1,
		w=750,
		h=420,
		fg_color=menu_screen.fg_color(),
		bg_color=menu_screen.bg_color(),
		rows=2,
		cols=3,
		controls=[mainscreen_btn,spinscreen_btn,test_btn1,test_btn2,lbl0,mini_grid]
		)

menu_grid.center()
menu_grid.middle()
mini_grid.position()

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
		onTap=main_screen.active,
		onTapArgs=[True],
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
		onTapArgs=['Got 1!'],
		onTap=display_input.change
		)

t2 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Toggle 2',
		datatype=t_datatype.text,
		onTapArgs=['Got 2!'],
		onTap=display_input.change
		)

t3 = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Enable 1',
		selected=True,
		onSelectArgs=['_selected'],
		onSelect=t1.enabled
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

btn = Button(
		border=5,
		size=3,
		fg_color=bg,
		bg_color=fg,
		text='EXIT',
		onTap=main_screen.active,
		onTapArgs=[True]
		)

btn.top(50)
btn.right()

toggle_screen.controls([display_input,tgrid,btn])

###############	listbx_screen controls ###############
fg = listbox_screen.fg_color()
bg = listbox_screen.bg_color()

lbl= Label(
		border=0,
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Select...'
		)

t1 = Toggle(
		size=2,
		fg_color=RA8875_YELLOW,
		bg_color=bg,
		text='Item 1',
		datatype=t_datatype.text,
		value='Got 1!'
		)

t2 = Toggle(
		size=2,
		fg_color=RA8875_YELLOW,
		bg_color=bg,
		text='Item 2',
		datatype=t_datatype.text,
		value='Got 2!'
		)

t3 = Toggle(
		size=2,
		fg_color=RA8875_YELLOW,
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
		w=400,
		h=350
		)

lbox.center(550)
lbox.middle()

btn = Button(
		border=2,
		size=3,
		w=50,
		h=50,
		fg_color=fg,
		bg_color=bg,
		text='OK',
		onTap=main_screen.active,
		onTapArgs=[True]
		)

btn.center(150)
btn.middle(350)

en = Toggle(
		size=2,
		fg_color=fg,
		bg_color=bg,
		text='Enable',
		selected=True,
		onSelectArgs=['_selected'],
		onSelect=lbox.enabled
		)

en.top(50)
en.left()

listbox_screen.controls([en,lbl,lbox,btn])




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