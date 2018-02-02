# Port of Adafruit_SSD1306.cpp LCD display library - 128 x 64 I2C only
import smbus
from Adafruit_GFX import *

BLACK = 0
WHITE = 1

SSD1306_LCDWIDTH=128
SSD1306_LCDHEIGHT=64

SSD1306_SETCONTRAST =0x81
SSD1306_DISPLAYALLON_RESUME =0xA4
SSD1306_DISPLAYALLON =0xA5
SSD1306_NORMALDISPLAY =0xA6
SSD1306_INVERTDISPLAY =0xA7
SSD1306_DISPLAYOFF =0xAE
SSD1306_DISPLAYON =0xAF

SSD1306_SETDISPLAYOFFSET =0xD3
SSD1306_SETCOMPINS =0xDA

SSD1306_SETVCOMDETECT =0xDB

SSD1306_SETDISPLAYCLOCKDIV =0xD5
SSD1306_SETPRECHARGE =0xD9

SSD1306_SETMULTIPLEX =0xA8

SSD1306_SETLOWCOLUMN =0x00
SSD1306_SETHIGHCOLUMN =0x10

SSD1306_SETSTARTLINE =0x40

SSD1306_MEMORYMODE =0x20

SSD1306_COMSCANINC =0xC0
SSD1306_COMSCANDEC =0xC8

SSD1306_SEGREMAP =0xA0

SSD1306_CHARGEPUMP =0x8D

SSD1306_EXTERNALVCC =0x1
SSD1306_SWITCHCAPVCC =0x2

# Scrolling #defines
SSD1306_ACTIVATE_SCROLL =0x2F
SSD1306_DEACTIVATE_SCROLL =0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA =0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL =0x26
SSD1306_LEFT_HORIZONTAL_SCROLL =0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL =0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL =0x2A

# the memory buffer for the LCD
buffer = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80,
0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x80, 0x80, 0xC0, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x80, 0xC0, 0xE0, 0xF0, 0xF8, 0xFC, 0xF8, 0xE0, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x80,
0x80, 0x80, 0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x80, 0x80, 0x80, 0x00, 0xFF,
0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x80, 0x80, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00,
0x80, 0xFF, 0xFF, 0x80, 0x80, 0x00, 0x80, 0x80, 0x00, 0x80, 0x80, 0x80, 0x80, 0x00, 0x80, 0x80,
0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00, 0x8C, 0x8E, 0x84, 0x00, 0x00, 0x80, 0xF8,
0xF8, 0xF8, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xE0, 0xE0, 0xC0, 0x80,
0x00, 0xE0, 0xFC, 0xFE, 0xFF, 0xFF, 0xFF, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFE, 0xFF, 0xC7, 0x01, 0x01,
0x01, 0x01, 0x83, 0xFF, 0xFF, 0x00, 0x00, 0x7C, 0xFE, 0xC7, 0x01, 0x01, 0x01, 0x01, 0x83, 0xFF,
0xFF, 0xFF, 0x00, 0x38, 0xFE, 0xC7, 0x83, 0x01, 0x01, 0x01, 0x83, 0xC7, 0xFF, 0xFF, 0x00, 0x00,
0x01, 0xFF, 0xFF, 0x01, 0x01, 0x00, 0xFF, 0xFF, 0x07, 0x01, 0x01, 0x01, 0x00, 0x00, 0x7F, 0xFF,
0x80, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x7F, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x01, 0xFF,
0xFF, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x03, 0x0F, 0x3F, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE7, 0xC7, 0xC7, 0x8F,
0x8F, 0x9F, 0xBF, 0xFF, 0xFF, 0xC3, 0xC0, 0xF0, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC, 0xFC, 0xFC,
0xFC, 0xFC, 0xFC, 0xFC, 0xFC, 0xF8, 0xF8, 0xF0, 0xF0, 0xE0, 0xC0, 0x00, 0x01, 0x03, 0x03, 0x03,
0x03, 0x03, 0x01, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x03, 0x03, 0x03, 0x01, 0x01,
0x03, 0x01, 0x00, 0x00, 0x00, 0x01, 0x03, 0x03, 0x03, 0x03, 0x01, 0x01, 0x03, 0x03, 0x00, 0x00,
0x00, 0x03, 0x03, 0x00, 0x00, 0x00, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
0x03, 0x03, 0x03, 0x03, 0x03, 0x01, 0x00, 0x00, 0x00, 0x01, 0x03, 0x01, 0x00, 0x00, 0x00, 0x03,
0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x80, 0xC0, 0xE0, 0xF0, 0xF9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x3F, 0x1F, 0x0F,
0x87, 0xC7, 0xF7, 0xFF, 0xFF, 0x1F, 0x1F, 0x3D, 0xFC, 0xF8, 0xF8, 0xF8, 0xF8, 0x7C, 0x7D, 0xFF,
0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x0F, 0x07, 0x00, 0x30, 0x30, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0xFE, 0xFE, 0xFC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xC0, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x30, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0xC0, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0x3F, 0x1F,
0x0F, 0x07, 0x1F, 0x7F, 0xFF, 0xFF, 0xF8, 0xF8, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0xF8, 0xE0,
0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFE, 0xFE, 0x00, 0x00,
0x00, 0xFC, 0xFE, 0xFC, 0x0C, 0x06, 0x06, 0x0E, 0xFC, 0xF8, 0x00, 0x00, 0xF0, 0xF8, 0x1C, 0x0E,
0x06, 0x06, 0x06, 0x0C, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xFE, 0xFE, 0x00, 0x00, 0x00, 0x00, 0xFC,
0xFE, 0xFC, 0x00, 0x18, 0x3C, 0x7E, 0x66, 0xE6, 0xCE, 0x84, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0x06,
0x06, 0xFC, 0xFE, 0xFC, 0x0C, 0x06, 0x06, 0x06, 0x00, 0x00, 0xFE, 0xFE, 0x00, 0x00, 0xC0, 0xF8,
0xFC, 0x4E, 0x46, 0x46, 0x46, 0x4E, 0x7C, 0x78, 0x40, 0x18, 0x3C, 0x76, 0xE6, 0xCE, 0xCC, 0x80,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x01, 0x07, 0x0F, 0x1F, 0x1F, 0x3F, 0x3F, 0x3F, 0x3F, 0x1F, 0x0F, 0x03,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x00, 0x00,
0x00, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x00, 0x00, 0x03, 0x07, 0x0E, 0x0C,
0x18, 0x18, 0x0C, 0x06, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x01, 0x0F, 0x0E, 0x0C, 0x18, 0x0C, 0x0F,
0x07, 0x01, 0x00, 0x04, 0x0E, 0x0C, 0x18, 0x0C, 0x0F, 0x07, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x00,
0x00, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x07,
0x07, 0x0C, 0x0C, 0x18, 0x1C, 0x0C, 0x06, 0x06, 0x00, 0x04, 0x0E, 0x0C, 0x18, 0x0C, 0x0F, 0x07,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

class SSD1306(GFX):
	# the most basic function, set a single pixel
	def drawPixel(self,x,y,color):
		if ((x < 0) or (x >= self.width()) or (y < 0) or (y >= self.height())):
			return

		# print str(x) + ':' + str(y)

		rotation = self.getRotation()
		if rotation==1:
			x,y = y,x
			x = self.WIDTH-x-1
		if rotation==2:
			x = self.WIDTH-x-1
			y = self.HEIGHT-y-1
		if rotation==3:
			x,y = y,x
			y = self.HEIGHT-y-1

		if (color==WHITE):
			# print 'buffer[' + str(x+ (y/8)*SSD1306_LCDWIDTH) + '] = ' + bin(buffer[x+ (y/8)*SSD1306_LCDWIDTH]) + '|' + bin((1<<(y%8)))	
			buffer[x+ (y/8)*SSD1306_LCDWIDTH] |= (1<<(y%8))
		else:
			buffer[x+ (y/8)*SSD1306_LCDWIDTH] &= (~(1<<(y%8)) & 0xFF)


	# initializer for I2C - we only indicate the reset pin!
	def __init__(self,reset):
		GFX.__init__(self,SSD1306_LCDWIDTH,SSD1306_LCDHEIGHT)
		self.rst = reset

	def begin(self,vccstate,i2caddr):
		self._i2caddr = i2caddr;

		self.bus = smbus.SMBus(3)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

		self.ssd1306_command(SSD1306_DISPLAYOFF)                    # 0xAE
		#    self.ssd1306_command(0x00)#---set low column address
		#    self.ssd1306_command(0x10)#---set high column address
		self.ssd1306_command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
		self.ssd1306_command(0x80)                                  # the suggested ratio 0x80
		self.ssd1306_command(SSD1306_SETMULTIPLEX)                  # 0xA8
		self.ssd1306_command(0x3F)
		self.ssd1306_command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
		self.ssd1306_command(0x0)                                   # no offset
		self.ssd1306_command(SSD1306_SETSTARTLINE | 0x0)            # line #0
		self.ssd1306_command(SSD1306_CHARGEPUMP)                    # 0x8D
		if vccstate == SSD1306_EXTERNALVCC:
			self.ssd1306_command(0x10)
		else:
			self.ssd1306_command(0x14)
		self.ssd1306_command(SSD1306_MEMORYMODE)                    # 0x20
		self.ssd1306_command(0x00)                                  # 0x0 act like ks0108
		self.ssd1306_command(SSD1306_SEGREMAP | 0x1)
		self.ssd1306_command(SSD1306_COMSCANDEC)
		self.ssd1306_command(SSD1306_SETCOMPINS)                    # 0xDA
		self.ssd1306_command(0x12)
		self.ssd1306_command(SSD1306_SETCONTRAST)                   # 0x81
		if vccstate == SSD1306_EXTERNALVCC:
			self.ssd1306_command(0x9F)
		else:
			self.ssd1306_command(0xCF)
		self.ssd1306_command(SSD1306_SETPRECHARGE)                  # 0xd9
		if vccstate == SSD1306_EXTERNALVCC:
			self.ssd1306_command(0x22)
		else:
			self.ssd1306_command(0xF1)
		self.ssd1306_command(SSD1306_SETVCOMDETECT)                 # 0xDB
		self.ssd1306_command(0x40)
		self.ssd1306_command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
		self.ssd1306_command(SSD1306_NORMALDISPLAY)                 # 0xA6

		self.ssd1306_command(0xb0)
		self.ssd1306_command(0x10)
		self.ssd1306_command(0x01)#Set original position to (0,0)

		self.ssd1306_command(SSD1306_DISPLAYON)#--turn on oled panel

	def invertDisplay(self, i):
		if i:
			self.ssd1306_command(SSD1306_INVERTDISPLAY)
		else:
			self.ssd1306_command(SSD1306_NORMALDISPLAY)

	def ssd1306_command(self,c):
		# print str(hex(self._i2caddr)) + '-' + str(hex(0x00)) + '-' + str(hex(c))
		self.bus.write_byte_data(self._i2caddr, 0x00, c)
		return

	# startscrollright
	# Activate a right handed scroll for rows start through stop
	# Hint, the display is 16 rows tall. To scroll the whole display, run:
	# display.scrollright(0x00, 0x0F) 
	def startscrollright(self, start, stop):
		self.ssd1306_command(SSD1306_RIGHT_HORIZONTAL_SCROLL)
		self.ssd1306_command(0X00)
		self.ssd1306_command(start)
		self.ssd1306_command(0X00)
		self.ssd1306_command(stop)
		self.ssd1306_command(0X01)
		self.ssd1306_command(0XFF)
		self.ssd1306_command(SSD1306_ACTIVATE_SCROLL)

	# startscrollleft
	# Activate a right handed scroll for rows start through stop
	# Hint, the display is 16 rows tall. To scroll the whole display, run:
	# display.scrollright(0x00, 0x0F) 
	def startscrollleft(self, start, stop):
		self.ssd1306_command(SSD1306_LEFT_HORIZONTAL_SCROLL)
		self.ssd1306_command(0X00)
		self.ssd1306_command(start)
		self.ssd1306_command(0X00)
		self.ssd1306_command(stop)
		self.ssd1306_command(0X01)
		self.ssd1306_command(0XFF)
		self.ssd1306_command(SSD1306_ACTIVATE_SCROLL)

	# startscrolldiagright
	# Activate a diagonal scroll for rows start through stop
	# Hint, the display is 16 rows tall. To scroll the whole display, run:
	# display.scrollright(0x00, 0x0F) 
	def startscrolldiagright(self, start, stop):
		self.ssd1306_command(SSD1306_SET_VERTICAL_SCROLL_AREA)	
		self.ssd1306_command(0X00)
		self.ssd1306_command(SSD1306_LCDHEIGHT)
		self.ssd1306_command(SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL)
		self.ssd1306_command(0X00)
		self.ssd1306_command(start)
		self.ssd1306_command(0X00)
		self.ssd1306_command(stop)
		self.ssd1306_command(0X01)
		self.ssd1306_command(SSD1306_ACTIVATE_SCROLL)

	# startscrolldiagleft
	# Activate a diagonal scroll for rows start through stop
	# Hint, the display is 16 rows tall. To scroll the whole display, run:
	# display.scrollright(0x00, 0x0F) 
	def startscrolldiagleft(self, start, stop):
		self.ssd1306_command(SSD1306_SET_VERTICAL_SCROLL_AREA)	
		self.ssd1306_command(0X00)
		self.ssd1306_command(SSD1306_LCDHEIGHT)
		self.ssd1306_command(SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL)
		self.ssd1306_command(0X00)
		self.ssd1306_command(start)
		self.ssd1306_command(0X00)
		self.ssd1306_command(stop)
		self.ssd1306_command(0X01)
		self.ssd1306_command(SSD1306_ACTIVATE_SCROLL)

	def stopscroll(self):
		self.ssd1306_command(SSD1306_DEACTIVATE_SCROLL)

	def ssd1306_data(self, c):
		# I2C
		control = 0x40   # Co = 0, D/C = 1
		self.bus.write_byte_data(self._i2caddr, control, c)

	def display(self):
		self.ssd1306_command(SSD1306_SETLOWCOLUMN | 0x0)  # low col = 0
		self.ssd1306_command(SSD1306_SETHIGHCOLUMN | 0x0)  # hi col = 0
		self.ssd1306_command(SSD1306_SETSTARTLINE | 0x0) # line #0

		control = 0x40   # Co = 0, D/C = 1
		# for i in range(SSD1306_LCDWIDTH*SSD1306_LCDHEIGHT/8):
			# send a bunch of data in one xmission
			# print str(hex(self._i2caddr)) + '-' + str(hex(0x40)) + '-' + str(hex(buffer[i]))
			# self.bus.write_byte_data(self._i2caddr, control, buffer[i])

		for i in range(0,SSD1306_LCDWIDTH*SSD1306_LCDHEIGHT/8,32):
			self.bus.write_i2c_block_data(self._i2caddr, control, buffer[i:i+32])

	# clear everything
	def clearDisplay(self):
		for i in range(SSD1306_LCDWIDTH*SSD1306_LCDHEIGHT/8):
			buffer[i]=0
