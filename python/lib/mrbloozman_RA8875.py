import CHIP_IO.GPIO as GPIO
from Adafruit_RA8875 import *
import enum

class t_screen(enum.Enum):
	main = 0
	menu = 1
	buttons = 2
	toggles = 3
	listbox = 4
	spinbox = 5
	image = 6

class t_datatype(enum.Enum):
	text = 0
	number = 1
	boolean = 2
	submit = 3

# common class for all controls
class Control:
	def __init__(self,**kwargs):
		self._parent = kwargs['parent']

		tftSearch = self._parent
		while '_tft' not in vars(tftSearch):
			tftSearch = tftSearch._parent
		self._tft = tftSearch._tft
		
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
			self._fg_color = self._parent.fg_color()

		if 'bg_color' in kwargs:
			self._bg_color = kwargs['bg_color']
		else:
			self._bg_color = self._parent.bg_color()

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
			self._w = 0

		if 'h' in kwargs:
			self._h = int(kwargs['h'])
		else:
			self._h = 0

		if 'border' in kwargs:
			self._border = int(kwargs['border'])
		else:
			self._border = 1

		if 'padding' in kwargs:
			self.padding(int(kwargs['padding']))
		else:
			self.padding(0)


		self._parent.addControl(self)

		try:
			if len(self._parent.controls())==(self._parent._rows*self._parent._cols):
				self._parent.position()
		except AttributeError:
			pass

	def padding(self,p):
		if p:
			self._padding = int(p)
		elif p==0:
			self._padding = 0
		minw = (self._border*2)+(self._padding*2)+self.text_width()
		minh = (self._border*2)+(self._padding*2)+self.text_height()
		if self._w < minw:
			self._w = minw
		if self._h < minh:
			self._h = minh
		return self._padding

	def skip(self,*args):
		pass

	def text(self,t=None):
		if t:
			self._text = str(t)
		return self._text

	def border(self,b=None):
		if b:
			self._border = int(b)
		elif b==0:
			self._border = 0
		return self._border

	def text_width(self):
		return 8*len(self._text)*(1+self._size)

	def text_height(self):
		return 16*(1+self._size)

	def size(self,s=None):
		if s:
			self._size = int(s)
		elif s==0:
			self._size = 0
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
		elif fg_color==0:
			self._fg_color = 0
		return self._fg_color

	def bg_color(self,bg_color=None):
		if bg_color:
			self._bg_color = int(bg_color)
		elif bg_color==0:
			self._bg_color=0
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
			x = int(self._tft.width()/2)
		self._x = x-int(self._w/2)

	def right(self,x=None):
		if x:
			x = int(x)
		else:
			x = self._tft.width()
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
			y = int(self._tft.height()/2)
		self._y = y-int(self._h/2)

	def bottom(self,y=None):
		if y:
			y = int(y)
		else:
			y = self._tft.height()
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
		nw = self._w * 1024 / self._tft.width()	# normalized width
		nh = self._h * 1024 / self._tft.height()	# normalized height
		nx = self._x * 1024 / self._tft.width()	# normalized x position
		ny = self._y * 1024 / self._tft.height()	# normalized y position
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
		self._tft.graphicsMode()
		self._tft.fillRect(self._x,self._y,self._w,self._h,self.bg_color())
		for b in range(self._border):
			self._tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self.fg_color())
		self._tft.textMode()
		self._tft.textColor(self.fg_color(),self.bg_color())
		# setting for center/middle of rect
		self._tft.textSetCursor(self._x+int(self._w/2)-int(self.text_width()/2),self._y+int(self._h/2)-int(self.text_height()/2))
		self._tft.textEnlarge(self._size)
		self._tft.textWrite(self._text,0)
		self._tft.graphicsMode()
		self._onRender(*self.listArgs(*self._onRenderArgs))
		
# do I need multi-line labels?
class Label(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)
		if 'border' not in kwargs:
			self.border(0)

class Grid(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)
		self._rows=int(kwargs['rows'])
		self._cols=int(kwargs['cols'])

		# if 'controls' in kwargs:
		# 	self._controls = kwargs['controls']
		# else:
		self._controls = []

		# if 'fg_color' in kwargs:
		# 	for c in self._controls:
		# 		c.fg_color(kwargs['fg_color'])

		# if 'bg_color' in kwargs:
		# 	for c in self._controls:
		# 		c.bg_color(kwargs['bg_color'])

		# if 'border' in kwargs:
		# 	for c in self._controls:
		# 		c.border(kwargs['border'])

		# self.position()

	def position(self):
		for r in range(self._rows):
			for c in range(self._cols):
				i = c+(r*self._cols)
				self._controls[i].x(self._x+int(c*self._w/self._cols))
				self._controls[i].y(self._y+int(r*self._h/self._rows))
				self._controls[i].w(int(self._w/self._cols))
				self._controls[i].h(int(self._h/self._rows))

				try:
					self._controls[i].position()
				except AttributeError:
					pass

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

	def addControl(self,c):
		self._controls.append(c)

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

		Control.__init__(self,**kwargs)

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
			# self._onRender(*self.listArgs(*self._onRenderArgs))
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
		self._tft.graphicsMode()
		self._tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		for b in range(self._border):
			self._tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self.fg_color())
		self._tft.textMode()
		self._tft.textColor(self.fg_color(),bg_color)
		# setting for center/middle of rect
		self._tft.textSetCursor(self._x+int(self._w/2)-int(self.value_width()/2),self._y+int(self._h/2)-int(self.value_height()/2))
		self._tft.textEnlarge(self._size)
		self._tft.textWrite(str(self._value),0)
		self._tft.graphicsMode()
		self._onRender(*self.listArgs(*self._onRenderArgs))

class Button(Input):
	def __init__(self,**kwargs):
		Input.__init__(self,**kwargs)
		
	def render(self):
		if self._enabled:
			bg_color = self.bg_color()
		else:
			bg_color = RA8875_BLACK		# probably will need a more clear disabled style i.e. gray, italic, strikethrough, etc
		self._tft.graphicsMode()
		self._tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		for b in range(self._border):
			self._tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self.fg_color())
		self._tft.textMode()
		self._tft.textColor(self.fg_color(),bg_color)
		# setting for center/middle of rect
		self._tft.textSetCursor(self._x+int(self._w/2)-int(self.value_width()/2),self._y+int(self._h/2)-int(self.value_height()/2))
		self._tft.textEnlarge(self._size)
		self._tft.textWrite(str(self._text),0)
		self._tft.graphicsMode()
		self._onRender(*self.listArgs(*self._onRenderArgs))

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
			self._onSelect = self.render

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
		if self._selected:
			s=True
		else:
			s=False
		if Button.tapped(self,touchPoint):
			self.selected(not s)
			# debug(self)

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
			# onChange=self.render
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
		self._tft.graphicsMode()
		self._tft.fillRect(self._x,self._y,self._w,self._h,bg_color)
		self._tft.drawRect(self._x,self._y,self._w,self._h,self._fg_color)
		self._label.render()
		self._input.render()
		self._upBtn.render()
		self._dnBtn.render()

	def tapped(self,touchPoint):
		self._upBtn.tapped(touchPoint)
		self._dnBtn.tapped(touchPoint)
		return Input.tapped(self,touchPoint)

class ListboxItem(Toggle):
	def __init__(self,**kwargs):
		Toggle.__init__(self,**kwargs)

	def tapped(self,touchPoint):
		return Button.tapped(self,touchPoint)

# Listbox is a container for Toggle instances - toggles callbacks will be overwritten to control the listbox value
class Listbox(Grid,Input):
	def __init__(self,**kwargs):
		kwargs['cols']=1
		if 'rows' in kwargs:
			self._rows=kwargs['rows']

		Grid.__init__(self,**kwargs)
		Input.__init__(self,**kwargs)

	def addControl(self,t):
		self._controls.append(t)
		i = len(self._controls)-1
		self.controls()[i]._onTap = self.change
		self.controls()[i]._onTapArgs = ['_value']
		# debug(self.controls()[i])

	def value(self,val=None):
		# print val
		if val or val==0:
			for t in self._controls:
				if val == t.value():
					t._selected=True
					# print val
				else:
					t._selected=False
		return Input.value(self,val)

	def enabled(self,en=None):
		if en or en==False:
			for c in self.controls():
				c.enabled(en)
		return Input.enabled(self,en)

class Image(Control):
	def __init__(self,**kwargs):
		Control.__init__(self,**kwargs)

		if 'src' in kwargs:
			self._src = kwargs['src']
		else:
			self._src = []

		if 'transparent' in kwargs:
			self._transparent = bool(kwargs['transparent'])
		else:
			self._transparent = False

	def transparent(self,t=None):
		if t:
			self._transparent = bool(t)
		elif t==False:
			self._transparent = False
		return self._transparent

	def src(self,s=None):
		if s:
			self._src = s
		return self._src

	def render(self):
		self._tft.graphicsMode()
		self._tft.fillRect(self._x,self._y,self._w,self._h,self.bg_color())
		for b in range(self._border):
			self._tft.drawRect(self._x+b,self._y+b,self._w-(2*b),self._h-(2*b),self.fg_color())
		# for r in range(self._h):
		# 	line = []
		# 	self._tft.setXY(self._x,self._y+r)
		# 	self._tft.writeCommand(RA8875_MRWC)
		# 	for c in range(self._w):
		# 		px = self._src[(r*self._w)+c]
		# 		if px == 0xFFFF:
		# 			px = self.bg_color()
		# 		line.append((px >> 8))
		# 		line.append(px)

		# 	GPIO.output(self._tft._cs, GPIO.LOW)
		# 	self._tft.spi.xfer2([RA8875_DATAWRITE]+line)
		# 	GPIO.output(self._tft._cs, GPIO.HIGH)

		# Set active window X 
		self._tft.writeReg(RA8875_HSAW0, (self._x & 0xFF))                                        # horizontal start point
		self._tft.writeReg(RA8875_HSAW1, (self._x >> 8))
		self._tft.writeReg(RA8875_HEAW0, (self._x+self._w - 1) & 0xFF)            # horizontal end point
		self._tft.writeReg(RA8875_HEAW1, (self._x+self._w - 1) >> 8)

		# Set active window Y 
		self._tft.writeReg(RA8875_VSAW0, (self._y & 0xFF))                                        # vertical start point
		self._tft.writeReg(RA8875_VSAW1, (self._y >> 8))  
		self._tft.writeReg(RA8875_VEAW0, (self._y+self._h - 1) & 0xFF)           # horizontal end point
		self._tft.writeReg(RA8875_VEAW1, (self._y+self._h - 1) >> 8)

		self._tft.setXY(self._x,self._y)
		self._tft.writeCommand(RA8875_MRWC)

		mem = []
		for px in self._src:
			if self._transparent and (px==0xFFFF):
				px = self.bg_color()
			mem.append((px >> 8))
			mem.append(px)

		for i in xrange(0,len(mem),4095):
			GPIO.output(self._tft._cs, GPIO.LOW)
			self._tft.spi.xfer2([RA8875_DATAWRITE]+mem[i:i+4095])
			GPIO.output(self._tft._cs, GPIO.HIGH)

		# Set active window X 
		self._tft.writeReg(RA8875_HSAW0, 0)                                        # horizontal start point
		self._tft.writeReg(RA8875_HSAW1, 0)
		self._tft.writeReg(RA8875_HEAW0, (self._tft.width() - 1) & 0xFF)            # horizontal end point
		self._tft.writeReg(RA8875_HEAW1, (self._tft.width() - 1) >> 8)

		# Set active window Y 
		self._tft.writeReg(RA8875_VSAW0, 0)                                        # vertical start point
		self._tft.writeReg(RA8875_VSAW1, 0)  
		self._tft.writeReg(RA8875_VEAW0, (self._tft.height() - 1) & 0xFF)           # horizontal end point
		self._tft.writeReg(RA8875_VEAW1, (self._tft.height() - 1) >> 8)

		self._onRender(*self.listArgs(*self._onRenderArgs))

# Common class for screens
class Screen:
	def __init__(self,**kwargs):
		self._id = kwargs['id']
		self._active = False
		self._parent = kwargs['parent']

		self._parent.addScreen(self)

		tftSearch = self._parent
		while '_tft' not in vars(tftSearch):
			tftSearch = tftSearch._parent
		self._tft = tftSearch._tft

		if 'fg_color' in kwargs:
			self._fg_color = kwargs['fg_color']
		else:
			self._fg_color = RA8875_WHITE

		if 'bg_color' in kwargs:
			self._bg_color = kwargs['bg_color']
		else:
			self._bg_color = RA8875_BLACK

		if 'controls' in kwargs:
			self._controls = kwargs['controls']
		else:
			self._controls = []

	def id(self):
		return self._id

	def fg_color(self,fg=None):
		if fg:
			self._fg_color = fg
		elif fg==0:
			self._fg_color=0
		return self._fg_color

	def bg_color(self,bg=None):
		if bg:
			self._bg_color = bg
		elif bg==0:
			self._bg_color=0
		return self._bg_color

	def addControl(self,c):
		self._controls.append(c)

	def controls(self,controls=None):
		if controls:
			self._controls=controls
		return self._controls

	def active(self,x=None):
		# global status
		# global screens
		if x:
			self._parent.status()['screen'] = self._id
			for s in self._parent.screens():
				s.active(False)
			self._tft.graphicsMode()
			self._tft.fillScreen(self._bg_color)

			for c in self._controls:
				c.render()
			self._tft.graphicsMode()
			self._active = True
		else:
			self._active = False

class TouchDisplay:
	def __init__(self,**kwargs):
		# self._screen = -1
		self._screens = []
		self._intPin = kwargs['intPin']
		self._tft = kwargs['tft']
		self._status = {}


	def status(self):
		return self._status

	def screens(self):
		return self._screens

	def addScreen(self,s):
		self._screens.append(s)

	def getScreen(self,id):
		for s in self._screens:
			if s.id() == id:
				return s
		return False

	def handleInterrupt(self):
		while self._tft.touched():
			tr = self._tft.touchRead()
		s = self.getScreen(self._status['screen'])
		for c in s.controls():
			c.tapped(tr)

	def handleUpdate(self):
		s = self.getScreen(self._status['screen'])
		for c in s.controls():
			try:
				c.update()
			except AttributeError:
				pass

	def run(self):
		while True:
			try:
				if GPIO.input(self._intPin)==0:
					self.handleInterrupt()
				self.handleUpdate()

			except KeyboardInterrupt:
				self._tft.displayOn(False)
				GPIO.cleanup()
				raise