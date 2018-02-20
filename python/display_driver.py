import sys
sys.path.append('lib')
from Adafruit_RA8875 import *
from time import sleep
import CHIP_IO.GPIO as GPIO
import CHIP_IO.OverlayManager as OM
from img import *
import datetime
from mrbloozman_RA8875 import *

def debug(obj):
	for k in vars(obj).keys():
		print k + ': ' + str(vars(obj)[k])

class Clock(Input):
	def __init__(self,**kwargs):
		Input.__init__(self,**kwargs)
		self._nextUpdate=datetime.datetime.now()

	def update(self):
		dt = datetime.datetime.now()
		if dt >= self._nextUpdate:
			self.change(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S%z"))
			self._nextUpdate = dt+datetime.timedelta(seconds=1)

OM.load('SPI2')

RA8875_INT = 'XIO-P1'
RA8875_CS = 'XIO-P2'
RA8875_RESET = 'XIO-P3'



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

app = TouchDisplay(intPin=RA8875_INT,tft=tft)


###############	screens ###############
main_screen = Screen(
		parent=app,
		id=t_screen.main,
		fg_color=RA8875_YELLOW,
		bg_color=RA8875_BLACK
		)

menu_screen = Screen(
		parent=app,
		id=t_screen.menu,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLACK
		)

buttons_screen = Screen(
		parent=app,
		id=t_screen.buttons,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLACK
		)

toggles_screen = Screen(
		parent=app,
		id=t_screen.toggles,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLACK
		)

listbox_screen = Screen(
		parent=app,
		id=t_screen.listbox,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLACK
		)

spinbox_screen = Screen(
		parent=app,
		id=t_screen.spinbox,
		fg_color=RA8875_WHITE,
		bg_color=RA8875_BLACK
		)

image_screen = Screen(
		parent=app,
		id=t_screen.image,
		fg_color=RA8875_YELLOW,
		bg_color=RA8875_BLACK
		)

# screens = [main_screen,menu_screen,buttons_screen,toggles_screen,listbox_screen,spinbox_screen,image_screen]

####################################################
btn = Button(
		parent=main_screen,
		onTap=menu_screen.active,
		onTapArgs=[True],
		w=tft.width()-1,
		h=tft.height()-1,
		border=0
		)

welcome_lbl = Label(
		parent=main_screen,
		text='Welcome to the RA8875 touchscreen demo!',
		size=1
		)

welcome_lbl.left(10)
welcome_lbl.bottom(50)

instruction_lbl = Label(
		parent=main_screen,
		text='Touch anywhere on the screen to continue...',
		size=1
		)

instruction_lbl.left(10)
instruction_lbl.top(50)

clk = Clock(
		parent=main_screen,
		datatype=t_datatype.text,
		size=2,
		value='THIS IS JUST A PLACEHOLDER',
		border=0
		)

clk.center()
clk.middle()

# main_screen.controls([btn,welcome_lbl,instruction_lbl])

####################################################
heading_lbl = Label(
		parent=menu_screen,
		text='Choose wisely...',
		size=1
		)

heading_lbl.center()
heading_lbl.top(10)

choices_grid = Grid(
		parent=menu_screen,
		# controls = [buttons_btn,toggles_btn,listbox_btn,spinbox_btn],
		rows=2,
		cols=2,
		w=700,
		h=350,
		fg_color=RA8875_BLACK,
		bg_color=RA8875_CYAN,
		border=4
		)

buttons_btn = Button(
		parent=choices_grid,
		size=2,
		text='Buttons',
		onTap=buttons_screen.active,
		onTapArgs=[True]
		)

toggles_btn = Button(
		parent=choices_grid,
		size=2,
		text='Toggles',
		onTap=toggles_screen.active,
		onTapArgs=[True]
		)

listbox_btn = Button(
		parent=choices_grid,
		size=2,
		text='Listbox',
		onTap=listbox_screen.active,
		onTapArgs=[True]
		)

image_btn = Button(
		parent=choices_grid,
		size=2,
		text='Image',
		onTap=image_screen.active,
		onTapArgs=[True]
		)

choices_grid.center()
choices_grid.bottom(430)

# menu_screen.controls([heading_lbl,choices_grid])

####################################################
heading_lbl = Label(
		parent=buttons_screen,
		text='Choose your favorite color...',
		size=1,
		border=2,
		padding=5)

heading_lbl.top()
heading_lbl.left()

red_grid = Grid(
		parent=buttons_screen,
		# controls=[red_btn],
		rows=1,
		cols=1,
		h=150,
		w=200,
		fg_color=RA8875_RED,
		bg_color=RA8875_WHITE,
		border=5,
		onTap=buttons_screen.active,
		onTapArgs=[True]
		)

red_btn = Button(
		parent=red_grid,
		text='Red',
		size=2,
		onTap=buttons_screen.bg_color,
		onTapArgs=[RA8875_RED])

red_grid.left(50)
red_grid.middle()

green_grid = Grid(
		parent=buttons_screen,
		# controls=[green_btn],
		rows=1,
		cols=1,
		h=150,
		w=200,
		fg_color=RA8875_GREEN,
		bg_color=RA8875_WHITE,
		onTap=buttons_screen.active,
		onTapArgs=[True]
		)

green_btn = Button(
		parent=green_grid,
		text='Green',
		size=2,
		border=5,
		onTap=buttons_screen.bg_color,
		onTapArgs=[RA8875_GREEN])

green_grid.center()
green_grid.middle()

blue_grid = Grid(
		parent=buttons_screen,
		# controls=[blue_btn],
		rows=1,
		cols=1,
		h=150,
		w=200,
		fg_color=RA8875_BLUE,
		bg_color=RA8875_WHITE,
		onTap=buttons_screen.active,
		onTapArgs=[True]
		)

blue_btn = Button(
		parent=blue_grid,
		text='Blue',
		size=2,
		border=5,
		onTap=buttons_screen.bg_color,
		onTapArgs=[RA8875_BLUE])

blue_grid.right(750)
blue_grid.middle()

warning_lbl = Label(
		parent=buttons_screen,
		text='I cannot be held responsible for poor color choices.',
		size=0,
		padding=10
		)

warning_lbl.center()
warning_lbl.bottom()

exit_btn = Button(
		parent=buttons_screen,
		text='EXIT',
		size=3,
		padding=25,
		border=2,
		onTapArgs=[True],
		onTap=main_screen.active
		)

exit_btn.top()
exit_btn.right()

# buttons_screen.controls([
# 	heading_lbl,
# 	red_grid,
# 	green_grid,
# 	blue_grid,
# 	warning_lbl,
# 	exit_btn
# 	])

####################################################
msg_input = Input(
	parent=toggles_screen,
	size=3,
	w=375,
	h=150,
	fg_color=RA8875_YELLOW,
	border=0,
	value='',
	datatype=t_datatype.text,
	onTap=menu_screen.active,
	onTapArgs=[True]
	)

msg_input._onChange = msg_input.render

t1 = Toggle(
	parent=toggles_screen,
	text='Toggle me',
	size=2,
	fg_color=RA8875_YELLOW,
	bg_color=RA8875_BLUE,
	padding=50,
	onTap=msg_input.change,
	onTapArgs=['Ouch!']
	)

t2 = Toggle(
	parent=toggles_screen,
	text='Me too',
	size=2,
	padding=50,
	fg_color=RA8875_YELLOW,
	bg_color=RA8875_BLUE,
	enabled=False,
	onTapArgs=['Not again!'],
	onTap=msg_input.change,
	onSelect=t1.enabled, # does enabled render again?
	onSelectArgs=[False]
	)

t1._onSelect = t2.enabled
t1._onSelectArgs = ['_selected']

t1.center(200)
t1.top(50)

t2.center(200)
t2.top(250)

msg_input.middle()
msg_input.x(400)

# toggles_screen.controls([msg_input,t1,t2])
####################################################
lbl = Label(
	parent=listbox_screen,
	text='Change menu screen colors'
	)

fg_grid = Grid(
	parent=listbox_screen,
	rows=1,
	cols=2,
	w=700,
	h=200
	# controls=[fg_lbl,fg_lbox]
	)

fg_lbl = Label(
	parent=fg_grid,
	text='Foreground: ',
	size=1
	)

fg_lbox = Listbox(
	parent=fg_grid,
	rows=3,
	# value=menu_screen.fg_color(),
	# controls=[ft1,ft2,ft3],
	datatype=t_datatype.number
	)

ft1 = ListboxItem(
	parent=fg_lbox,
	text='White',
	size=1,
	value=RA8875_WHITE,
	datatype=t_datatype.number
	)

ft2 = ListboxItem(
	parent=fg_lbox,
	text='Green',
	size=1,
	value=RA8875_GREEN,
	datatype=t_datatype.number
	)

ft3 = ListboxItem(
	parent=fg_lbox,
	text='Yellow',
	size=1,
	value=RA8875_YELLOW,
	datatype=t_datatype.number
	)

fg_lbox.value(menu_screen.fg_color())
fg_lbox._onChange=menu_screen.fg_color
fg_lbox._onChangeArgs=['_value']


bg_grid = Grid(
	parent=listbox_screen,
	rows=1,
	cols=2,
	w=700,
	h=200
	# controls=[bg_lbl,bg_lbox]
	)

bg_lbl = Label(
	parent=bg_grid,
	text='Background: ',
	size=1
	)

bg_lbox = Listbox(
	parent=bg_grid,
	rows=3,
	# value=menu_screen.bg_color(),
	# controls=[bt1,bt2,bt3],
	datatype=t_datatype.number
	)

bt1 = ListboxItem(
	parent=bg_lbox,
	text='Black',
	size=1,
	value=RA8875_BLACK,
	datatype=t_datatype.number
	)

bt2 = ListboxItem(
	parent=bg_lbox,
	text='Red',
	size=1,
	value=RA8875_RED,
	datatype=t_datatype.number
	)

bt3 = ListboxItem(
	parent=bg_lbox,
	text='Blue',
	size=1,
	value=RA8875_BLUE,
	datatype=t_datatype.number
	)

bg_lbox.value(menu_screen.bg_color())
bg_lbox._onChange=menu_screen.bg_color
bg_lbox._onChangeArgs=['_value']

lbl.center()
lbl.top()

fg_grid.center()
fg_grid.top(25)

bg_grid.center()
bg_grid.top(250)

exit_btn = Button(
	parent=listbox_screen,
	text='MENU',
	size=0,
	h=75,
	w=75,
	onTap=menu_screen.active,
	onTapArgs=[True]
	)

exit_btn.left(75)
exit_btn.middle()

# listbox_screen.controls([lbl,fg_grid,bg_grid,exit_btn])


####################################################

lbl = Label(
	parent=image_screen,
	text='Image...',
	size=1,
	padding=10
	)

lbl.center()
lbl.top()

# goblin_img = NetPBM()
# goblin_img.load('static/img/Goblin.ppm')

# jedi_img = NetPBM()
# jedi_img.load('static/img/jedi-256x256.pgm')

makey_img = NetPBM()
makey_img.load('static/img/makey-190x200.ppm')

flame_img = NetPBM()
flame_img.load('static/img/flame-290x400.ppm')

img1 = Image(
	parent=image_screen,
	border=0,
	w=flame_img._width,
	h=flame_img._height,
	src=flame_img.export(),
	transparent=True,
   onTap=menu_screen.active,
   onTapArgs=[True]
   )

img1.left(50)
img1.middle()

img2 = Image(
	parent=image_screen,
	border=0,
	w=makey_img._width,
	h=makey_img._height,
	src=makey_img.export(),
	transparent=True,
   onTap=menu_screen.active,
   onTapArgs=[True]
   )

img2.right(750)
img2.middle()

####################################################

####################################################




####################################################



main_screen.active(True)


# app.addScreen(main_screen)
# app.addScreen(menu_screen)
# app.addScreen(buttons_screen)
# app.addScreen(toggles_screen)
# app.addScreen(listbox_screen)
# app.addScreen(spinbox_screen)
# app.addScreen(image_screen)

app.run()

GPIO.cleanup()