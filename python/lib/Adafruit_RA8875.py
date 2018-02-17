# port of Adafruit_RA8875.cpp
import time
import spidev
import CHIP_IO.GPIO as GPIO
from Adafruit_GFX import *
from Adafruit_RA8875_h import *

# spi_speed = 1000000

# def spi_begin()
# def spi_end()

######################################################################
# Constructor for a new RA8875 instance
# @args CS[in]  Location of the SPI chip select pin
# @args RST[in] Location of the reset pin
######################################################################

class Adafruit_RA8875(GFX):
	def __init__(self, CS, RST):
		GFX.__init__(self, 800, 480)
		self._cs = CS
		self._rst = RST

######################################################################
# Initialises the LCD driver and any HW required by the display

# @args s[in] The display size, which can be either:
#           'RA8875_480x272' (4.3" displays) r
#           'RA8875_800x480' (5" and 7" displays)
######################################################################

	def begin(self,s):
		self._size = s

		if self._size == RA8875sizes.RA8875_480x272:
			self._width = 480
			self._height = 272
		elif self._size == RA8875sizes.RA8875_800x480:
			self._width = 800
			self._height = 480
		else:
			return False

		

		# GPIO.setup('CSIPCK',GPIO.IN, pull_up_down=GPIO.PUD_UP)

		# pinMode(_cs, OUTPUT);
		GPIO.setup(self._cs, GPIO.OUT, initial=1)
		# digitalWrite(_cs, HIGH);
		# GPIO.output(self._cs, GPIO.HIGH)
		# pinMode(_rst, OUTPUT);
		GPIO.setup(self._rst, GPIO.OUT)
		# digitalWrite(_rst, LOW);
		GPIO.output(self._rst, GPIO.LOW)
		# delay(100);
		time.sleep(0.1)
		# digitalWrite(_rst, HIGH);
		GPIO.output(self._rst, GPIO.HIGH)
		# delay(100);
		time.sleep(0.1)

		self.spi = spidev.SpiDev()
		self.spi.open(32766, 0)
		# self.spi.max_speed_hz = 125000
		self.spi.max_speed_hz = 2000000
		self.spi.mode = 0b00
		# self.spi.cshigh = False
		# self.spi.lsbfirst = False
		# self.spi.no_cs = True



		x = self.readReg(0x00)
		# print hex(x)
		if x != 0x75:
			return False

		self.initialize();
		return True

######################################################################
# Performs a SW-based reset of the RA8875
######################################################################

	def softReset(self):
		self.writeCommand(RA8875_PWRR)
		self.writeData(RA8875_PWRR_SOFTRESET)
		self.writeData(RA8875_PWRR_NORMAL)

######################################################################
# Initialise the PLL
###########readReg###########################################################

	def PLLinit(self):
		if self._size == RA8875sizes.RA8875_480x272:
			self.writeReg(RA8875_PLLC1, RA8875_PLLC1_PLLDIV1 + 10)
			self.writeReg(RA8875_PLLC2, RA8875_PLLC2_DIV4)
		else:
			self.writeReg(RA8875_PLLC1, RA8875_PLLC1_PLLDIV1 + 10)
			self.writeReg(RA8875_PLLC2, RA8875_PLLC2_DIV4)

######################################################################
# Initialises the driver IC (clock setup, etc.)
######################################################################

	def initialize(self):
		self.PLLinit()
		self.writeReg(RA8875_SYSR, RA8875_SYSR_16BPP | RA8875_SYSR_MCU8)

		# Timing values
		# Set the correct values for the display being used 
		if self._size == RA8875sizes.RA8875_480x272:
			pixclk          = RA8875_PCSR_PDATL | RA8875_PCSR_4CLK
			hsync_nondisp   = 10
			hsync_start     = 8
			hsync_pw        = 48
			hsync_finetune  = 0
			vsync_nondisp   = 3
			vsync_start     = 8
			vsync_pw        = 10
		else: # (_size == RA8875_800x480)
			pixclk          = RA8875_PCSR_PDATL | RA8875_PCSR_2CLK
			hsync_nondisp   = 26
			hsync_start     = 32
			hsync_pw        = 96
			hsync_finetune  = 0
			vsync_nondisp   = 32
			vsync_start     = 23
			vsync_pw        = 2

		self.writeReg(RA8875_PCSR, pixclk)

		# Horizontal settings registers
		self.writeReg(RA8875_HDWR, (self._width / 8) - 1)                          # H width: (HDWR + 1) * 8 = 480
		self.writeReg(RA8875_HNDFTR, RA8875_HNDFTR_DE_HIGH + hsync_finetune)
		self.writeReg(RA8875_HNDR, (hsync_nondisp - hsync_finetune - 2)/8)    # H non-display: HNDR * 8 + HNDFTR + 2 = 10
		self.writeReg(RA8875_HSTR, hsync_start/8 - 1)                         # Hsync start: (HSTR + 1)*8 
		self.writeReg(RA8875_HPWR, RA8875_HPWR_LOW + (hsync_pw/8 - 1))        # HSync pulse width = (HPWR+1) * 8

		# Vertical settings registers 
		self.writeReg(RA8875_VDHR0, (self._height - 1) & 0xFF)
		self.writeReg(RA8875_VDHR1, (self._height - 1) >> 8)
		self.writeReg(RA8875_VNDR0, vsync_nondisp-1)                          # V non-display period = VNDR + 1
		self.writeReg(RA8875_VNDR1, vsync_nondisp >> 8)
		self.writeReg(RA8875_VSTR0, vsync_start-1)                            # Vsync start position = VSTR + 1
		self.writeReg(RA8875_VSTR1, vsync_start >> 8)
		self.writeReg(RA8875_VPWR, RA8875_VPWR_LOW + vsync_pw - 1)            # Vsync pulse width = VPWR + 1

		# Set active window X 
		self.writeReg(RA8875_HSAW0, 0)                                        # horizontal start point
		self.writeReg(RA8875_HSAW1, 0)
		self.writeReg(RA8875_HEAW0, (self._width - 1) & 0xFF)            # horizontal end point
		self.writeReg(RA8875_HEAW1, (self._width - 1) >> 8)

		# Set active window Y 
		self.writeReg(RA8875_VSAW0, 0)                                        # vertical start point
		self.writeReg(RA8875_VSAW1, 0)  
		self.writeReg(RA8875_VEAW0, (self._height - 1) & 0xFF)           # horizontal end point
		self.writeReg(RA8875_VEAW1, (self._height - 1) >> 8)

		# ToDo: Setup touch panel? 

		# Clear the entire window 
		self.writeReg(RA8875_MCLR, RA8875_MCLR_START | RA8875_MCLR_FULL)
		time.sleep(0.5) 

######################################################################
# Returns the display width in pixels
######################################################################

	def width(self):
		return self._width

######################################################################
# Returns the display height in pixels
######################################################################

	def height(self):
		return self._height

######################################################################
# Sets the display in text mode (as opposed to graphics mode)
######################################################################

	def textMode(self):
		# Set text mode
		self.writeCommand(RA8875_MWCR0)
		temp = self.readData()
		temp |= RA8875_MWCR0_TXTMODE # Set bit 7
		self.writeData(temp)

		# Select the internal (ROM) font
		self.writeCommand(0x21)
		temp = self.readData()
		temp &= ~((1<<7) | (1<<5)) # Clear bits 7 and 5
		self.writeData(temp)

######################################################################
# Sets the display in text mode (as opposed to graphics mode)

# @args x[in] The x position of the cursor (in pixels, 0..1023)
# @args y[in] The y position of the cursor (in pixels, 0..511)
######################################################################

	def textSetCursor(self, x, y):
		self.writeCommand(0x2A)
		self.writeData(x & 0xFF)
		self.writeCommand(0x2B)
		self.writeData(x >> 8)
		self.writeCommand(0x2C)
		self.writeData(y & 0xFF)
		self.writeCommand(0x2D)
		self.writeData(y >> 8)

######################################################################
# Sets the fore and background color when rendering text

# @args foreColor[in] The RGB565 color to use when rendering the text
# @args bgColor[in]   The RGB565 colot to use for the background
######################################################################

	def textColor(self, foreColor, bgColor):
		# Set Fore Color
		self.writeCommand(0x63)
		self.writeData((foreColor & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((foreColor & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((foreColor & 0x001f))

		# Set Background Color
		self.writeCommand(0x60)
		self.writeData((bgColor & 0xf800) >> 11)
		self.writeCommand(0x61)
		self.writeData((bgColor & 0x07e0) >> 5)
		self.writeCommand(0x62)
		self.writeData((bgColor & 0x001f))

		# Clear transparency flag
		self.writeCommand(0x22)
		temp = self.readData()
		temp &= ~(1<<6) # Clear bit 6
		self.writeData(temp)

######################################################################
# Sets the fore color when rendering text with a transparent bg

# @args foreColor[in] The RGB565 color to use when rendering the text
######################################################################

	def textTransparent(self, foreColor):
		# Set Fore Color
		self.writeCommand(0x63)
		self.writeData((foreColor & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((foreColor & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((foreColor & 0x001f))

		# Set transparency flag
		self.writeCommand(0x22)
		temp = self.readData()
		temp |= (1<<6) # Set bit 6
		self.writeData(temp) 

######################################################################
# Sets the text enlarge settings, using one of the following values:

# 0 = 1x zoom
# 1 = 2x zoom
# 2 = 3x zoom
# 3 = 4x zoom

# @args scale[in]   The zoom factor (0..3 for 1-4x zoom)
######################################################################

	def textEnlarge(self, scale):
		if scale > 3:
			scale = 3

		# Set font size flags
		self.writeCommand(0x22)
		temp = self.readData()
		temp &= ~(0xF) # Clears bits 0..3
		temp |= scale << 2
		temp |= scale
		self.writeData(temp)  

		self._textScale = scale

######################################################################
# Renders some text on the screen when in text mode

# @args buffer[in]    The buffer containing the characters to render
# @args len[in]       The size of the buffer in bytes
######################################################################

	def textWrite(self, buffer, ln): 
		if ln == 0:
			ln = len(buffer)
		self.writeCommand(RA8875_MRWC)

		for i in range(ln):
			self.writeData(ord(buffer[i]))

######################################################################
# Sets the display in graphics mode (as opposed to text mode)
######################################################################

	def graphicsMode(self):
		self.writeCommand(RA8875_MWCR0)
		temp = self.readData()
		temp &= ~RA8875_MWCR0_TXTMODE # bit #7
		self.writeData(temp)

######################################################################
# Waits for screen to finish by polling the status!
######################################################################
	
	def waitPoll(self, regname, waitflag):
		# Wait for the command to finish
		while True:
			temp = self.readReg(regname)
			# print 'waitPoll(' + hex(regname) + ','+hex(waitflag)+'): '+hex(temp)
			if not (temp & waitflag):
				return True
		return false # MEMEFIX: yeah i know, unreached! - add timeout?

######################################################################
# Sets the current X/Y position on the display before drawing

# @args x[in] The 0-based x location
# @args y[in] The 0-base y location
######################################################################

	def setXY(self, x, y):
		self.writeReg(RA8875_CURH0, x)
		self.writeReg(RA8875_CURH1, x >> 8)
		self.writeReg(RA8875_CURV0, y)
		self.writeReg(RA8875_CURV1, y >> 8)  

######################################################################
# HW accelerated function to push a chunk of raw pixel data

# @args num[in] The number of pixels to push
# @args p[in]   The pixel color to use
######################################################################

	def pushPixels(self, num, p):
		# digitalWrite(_cs, LOW);
		GPIO.output(self._cs, GPIO.LOW)
		self.spi.xfer2([RA8875_DATAWRITE])
		while num > 0:
			self.spi.xfer2([(p >> 8),p])
			num = num-1
		# digitalWrite(_cs, HIGH);
		GPIO.output(self._cs, GPIO.HIGH)

######################################################################

######################################################################

	def fillRect(self):
		self.writeCommand(RA8875_DCR)
		self.writeData(RA8875_DCR_LINESQUTRI_STOP | RA8875_DCR_DRAWSQUARE)
		self.writeData(RA8875_DCR_LINESQUTRI_START | RA8875_DCR_FILL | RA8875_DCR_DRAWSQUARE)

######################################################################
# Draws a single pixel at the specified location

# @args x[in]     The 0-based x location
# @args y[in]     The 0-base y location
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def drawPixel(self, x, y, color):
		# self.writeReg(RA8875_CURH0, x)
		# self.writeReg(RA8875_CURH1, x >> 8)
		# self.writeReg(RA8875_CURV0, y)
		# self.writeReg(RA8875_CURV1, y >> 8) 
		self.setXY(x,y) 
		self.writeCommand(RA8875_MRWC)
		# digitalWrite(_cs, LOW)
		GPIO.output(self._cs, GPIO.LOW)
		self.spi.xfer2([RA8875_DATAWRITE,(color >> 8),color])
		# digitalWrite(_cs, HIGH)
		GPIO.output(self._cs, GPIO.HIGH)

######################################################################
# Draws a HW accelerated line on the display

# @args x0[in]    The 0-based starting x location
# @args y0[in]    The 0-base starting y location
# @args x1[in]    The 0-based ending x location
# @args y1[in]    The 0-base ending y location
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def drawLine(self, x0, y0, x1, y1, color):
		# /* Set X */
		self.writeCommand(0x91)
		self.writeData(x0)
		self.writeCommand(0x92)
		self.writeData(x0 >> 8)

		# /* Set Y */
		self.writeCommand(0x93)
		self.writeData(y0) 
		self.writeCommand(0x94)
		self.writeData(y0 >> 8)

		# /* Set X1 */
		self.writeCommand(0x95)
		self.writeData(x1)
		self.writeCommand(0x96)
		self.writeData((x1) >> 8)

		# /* Set Y1 */
		self.writeCommand(0x97)
		self.writeData(y1) 
		self.writeCommand(0x98)
		self.writeData((y1) >> 8)

		# /* Set Color */
		self.writeCommand(0x63)
		self.writeData((color & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((color & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((color & 0x001f))

		# /* Draw! */
		self.writeCommand(RA8875_DCR)
		self.writeData(0x80)

		# /* Wait for the command to finish */
		self.waitPoll(RA8875_DCR, RA8875_DCR_LINESQUTRI_STATUS)

######################################################################

######################################################################

	def drawFastVLine(self, x, y, h, color):
		self.drawLine(x, y, x, y+h, color)

######################################################################

######################################################################

	def drawFastHLine(self, x, y, w, color):
		self.drawLine(x, y, x+w, y, color)

######################################################################
# Draws a HW accelerated rectangle on the display

# @args x[in]     The 0-based x location of the top-right corner
# @args y[in]     The 0-based y location of the top-right corner
# @args w[in]     The rectangle width
# @args h[in]     The rectangle height
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def drawRect(self, x, y, w, h, color):
		self.rectHelper(x, y, x+w, y+h, color, False)

######################################################################
# Draws a HW accelerated filled rectangle on the display

# @args x[in]     The 0-based x location of the top-right corner
# @args y[in]     The 0-based y location of the top-right corner
# @args w[in]     The rectangle width
# @args h[in]     The rectangle height
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def fillRect(self, x, y, w, h, color):
		self.rectHelper(x, y, x+w, y+h, color, True)

######################################################################
# Fills the screen with the spefied RGB565 color

# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def fillScreen(self, color):
		self.rectHelper(0, 0, self._width-1, self._height-1, color, True)

######################################################################
# Draws a HW accelerated circle on the display

# @args x[in]     The 0-based x location of the center of the circle
# @args y[in]     The 0-based y location of the center of the circle
# @args w[in]     The circle's radius
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def drawCircle(self, x0, y0, r, color):
		self.circleHelper(x0, y0, r, color, False)

######################################################################
# Draws a HW accelerated filled circle on the display

# @args x[in]     The 0-based x location of the center of the circle
# @args y[in]     The 0-based y location of the center of the circle
# @args w[in]     The circle's radius
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def fillCircle(self, x0, y0, r, color):
		self.circleHelper(x0, y0, r, color, True)

######################################################################
# Draws a HW accelerated triangle on the display

# @args x0[in]    The 0-based x location of point 0 on the triangle
# @args y0[in]    The 0-based y location of point 0 on the triangle
# @args x1[in]    The 0-based x location of point 1 on the triangle
# @args y1[in]    The 0-based y location of point 1 on the triangle
# @args x2[in]    The 0-based x location of point 2 on the triangle
# @args y2[in]    The 0-based y location of point 2 on the triangle
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def drawTriangle(self, x0, y0, x1, y1, x2, y2, color):
		self.triangleHelper(x0, y0, x1, y1, x2, y2, color, False)

######################################################################
# Draws a HW accelerated filled triangle on the display

# @args x0[in]    The 0-based x location of point 0 on the triangle
# @args y0[in]    The 0-based y location of point 0 on the triangle
# @args x1[in]    The 0-based x location of point 1 on the triangle
# @args y1[in]    The 0-based y location of point 1 on the triangle
# @args x2[in]    The 0-based x location of point 2 on the triangle
# @args y2[in]    The 0-based y location of point 2 on the triangle
# @args color[in] The RGB565 color to use when drawing the pixel
######################################################################

	def fillTriangle(self, x0, y0, x1, y1, x2, y2, color):
		self.triangleHelper(x0, y0, x1, y1, x2, y2, color, True)

######################################################################
# Draws a HW accelerated ellipse on the display

# @args xCenter[in]   The 0-based x location of the ellipse's center
# @args yCenter[in]   The 0-based y location of the ellipse's center
# @args longAxis[in]  The size in pixels of the ellipse's long axis
# @args shortAxis[in] The size in pixels of the ellipse's short axis
# @args color[in]     The RGB565 color to use when drawing the pixel
######################################################################

	def drawEllipse(self, xCenter, yCenter, longAxis, shortAxis, color):
		self.ellipseHelper(xCenter, yCenter, longAxis, shortAxis, color, False)

######################################################################
# Draws a HW accelerated filled ellipse on the display

# @args xCenter[in]   The 0-based x location of the ellipse's center
# @args yCenter[in]   The 0-based y location of the ellipse's center
# @args longAxis[in]  The size in pixels of the ellipse's long axis
# @args shortAxis[in] The size in pixels of the ellipse's short axis
# @args color[in]     The RGB565 color to use when drawing the pixel
######################################################################

	def fillEllipse(self, xCenter, yCenter, longAxis, shortAxis, color):
		self.ellipseHelper(xCenter, yCenter, longAxis, shortAxis, color, True)

######################################################################
# Draws a HW accelerated curve on the display

# @args xCenter[in]   The 0-based x location of the ellipse's center
# @args yCenter[in]   The 0-based y location of the ellipse's center
# @args longAxis[in]  The size in pixels of the ellipse's long axis
# @args shortAxis[in] The size in pixels of the ellipse's short axis
# @args curvePart[in] The corner to draw, where in clock-wise motion:
#                     0 = 180-270
#                     1 = 270-0
#                     2 = 0-90
#                     3 = 90-180
# @args color[in]     The RGB565 color to use when drawing the pixel
######################################################################

	def drawCurve(self, xCenter, yCenter, longAxis, shortAxis, curvePart, color):
 		self.curveHelper(xCenter, yCenter, longAxis, shortAxis, curvePart, color, False)

######################################################################
# Draws a HW accelerated filled curve on the display

# @args xCenter[in]   The 0-based x location of the ellipse's center
# @args yCenter[in]   The 0-based y location of the ellipse's center
# @args longAxis[in]  The size in pixels of the ellipse's long axis
# @args shortAxis[in] The size in pixels of the ellipse's short axis
# @args curvePart[in] The corner to draw, where in clock-wise motion:
#                     0 = 180-270
#                     1 = 270-0
#                     2 = 0-90
#                     3 = 90-180
# @args color[in]     The RGB565 color to use when drawing the pixel
######################################################################

	def fillCurve(self, xCenter, yCenter, longAxis, shortAxis, curvePart, color):
		self.curveHelper(xCenter, yCenter, longAxis, shortAxis, curvePart, color, True)

######################################################################
# Helper function for higher level circle drawing code
######################################################################

	def circleHelper(self, x0, y0, r, color, filled):
		# /* Set X */
		x0 = int(x0)
		self.writeCommand(0x99)
		self.writeData(x0)
		self.writeCommand(0x9a)
		self.writeData(x0 >> 8)

		# /* Set Y */
		y0 = int(y0)
		self.writeCommand(0x9b)
		self.writeData(y0) 
		self.writeCommand(0x9c)	   
		self.writeData(y0 >> 8)

		# /* Set Radius */
		self.writeCommand(0x9d)
		self.writeData(r)  

		# /* Set Color */
		self.writeCommand(0x63)
		self.writeData((color & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((color & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((color & 0x001f))

		# /* Draw! */
		self.writeCommand(RA8875_DCR)
		if filled:
			self.writeData(RA8875_DCR_CIRCLE_START | RA8875_DCR_FILL)
		else:
			self.writeData(RA8875_DCR_CIRCLE_START | RA8875_DCR_NOFILL)

		# /* Wait for the command to finish */
		self.waitPoll(RA8875_DCR, RA8875_DCR_CIRCLE_STATUS)

######################################################################
# Helper function for higher level rectangle drawing code
######################################################################

	def rectHelper(self, x, y, w, h, color, filled):
		# /* Set X */
		self.writeCommand(0x91)
		self.writeData(x)
		self.writeCommand(0x92)
		self.writeData(x >> 8)

		# /* Set Y */
		self.writeCommand(0x93)
		self.writeData(y) 
		self.writeCommand(0x94)	   
		self.writeData(y >> 8)

		# /* Set X1 */
		self.writeCommand(0x95)
		self.writeData(w)
		self.writeCommand(0x96)
		self.writeData((w) >> 8)

		# /* Set Y1 */
		self.writeCommand(0x97)
		self.writeData(h) 
		self.writeCommand(0x98)
		self.writeData((h) >> 8)

		# /* Set Color */
		self.writeCommand(0x63)
		self.writeData((color & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((color & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((color & 0x001f))

		# /* Draw! */
		self.writeCommand(RA8875_DCR)
		if filled:
			self.writeData(0xB0)
		else:
			self.writeData(0x90)

		# /* Wait for the command to finish */
		self.waitPoll(RA8875_DCR, RA8875_DCR_LINESQUTRI_STATUS)

######################################################################
# Helper function for higher level triangle drawing code
######################################################################

	def triangleHelper(self, x0, y0, x1, y1, x2, y2, color, filled):
		# /* Set Point 0 */
		self.writeCommand(0x91)
		self.writeData(x0)
		self.writeCommand(0x92)
		self.writeData(x0 >> 8)
		self.writeCommand(0x93)
		self.writeData(y0) 
		self.writeCommand(0x94)
		self.writeData(y0 >> 8)

		# /* Set Point 1 */
		self.writeCommand(0x95)
		self.writeData(x1)
		self.writeCommand(0x96)
		self.writeData(x1 >> 8)
		self.writeCommand(0x97)
		self.writeData(y1) 
		self.writeCommand(0x98)
		self.writeData(y1 >> 8)

		# /* Set Point 2 */
		self.writeCommand(0xA9)
		self.writeData(x2)
		self.writeCommand(0xAA)
		self.writeData(x2 >> 8)
		self.writeCommand(0xAB)
		self.writeData(y2) 
		self.writeCommand(0xAC)
		self.writeData(y2 >> 8)

		# /* Set Color */
		self.writeCommand(0x63)
		self.writeData((color & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((color & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((color & 0x001f))

		# /* Draw! */
		self.writeCommand(RA8875_DCR)
		if filled:
			self.writeData(0xA1)
		else:
			self.writeData(0x81)

		# /* Wait for the command to finish */
		self.waitPoll(RA8875_DCR, RA8875_DCR_LINESQUTRI_STATUS)

######################################################################
# Helper function for higher level ellipse drawing code
######################################################################

	def ellipseHelper(self, xCenter, yCenter, longAxis, shortAxis, color, filled):
		# /* Set Center Point */
		self.writeCommand(0xA5)
		self.writeData(xCenter)
		self.writeCommand(0xA6)
		self.writeData(xCenter >> 8)
		self.writeCommand(0xA7)
		self.writeData(yCenter) 
		self.writeCommand(0xA8)
		self.writeData(yCenter >> 8)

		# /* Set Long and Short Axis */
		self.writeCommand(0xA1)
		self.writeData(longAxis)
		self.writeCommand(0xA2)
		self.writeData(longAxis >> 8)
		self.writeCommand(0xA3)
		self.writeData(shortAxis) 
		self.writeCommand(0xA4)
		self.writeData(shortAxis >> 8)

		# /* Set Color */
		self.writeCommand(0x63)
		self.writeData((color & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((color & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((color & 0x001f))

		# /* Draw! */
		self.writeCommand(0xA0)
		if filled:
			self.writeData(0xC0)
		else:
			self.writeData(0x80)

		# /* Wait for the command to finish */
		self.waitPoll(RA8875_ELLIPSE, RA8875_ELLIPSE_STATUS)

######################################################################
# Helper function for higher level curve drawing code
######################################################################

	def curveHelper(self, xCenter, yCenter, longAxis, shortAxis, curvePart, color, filled):
		# /* Set Center Point */
		self.writeCommand(0xA5)
		self.writeData(xCenter)
		self.writeCommand(0xA6)
		self.writeData(xCenter >> 8)
		self.writeCommand(0xA7)
		self.writeData(yCenter) 
		self.writeCommand(0xA8)
		self.writeData(yCenter >> 8)

		# /* Set Long and Short Axis */
		self.writeCommand(0xA1)
		self.writeData(longAxis)
		self.writeCommand(0xA2)
		self.writeData(longAxis >> 8)
		self.writeCommand(0xA3)
		self.writeData(shortAxis) 
		self.writeCommand(0xA4)
		self.writeData(shortAxis >> 8)

		# /* Set Color */
		self.writeCommand(0x63)
		self.writeData((color & 0xf800) >> 11)
		self.writeCommand(0x64)
		self.writeData((color & 0x07e0) >> 5)
		self.writeCommand(0x65)
		self.writeData((color & 0x001f))

		# /* Draw! */
		self.writeCommand(0xA0)
		if filled:
			self.writeData(0xD0 | (curvePart & 0x03))
		else:
			self.writeData(0x90 | (curvePart & 0x03))

		# /* Wait for the command to finish */
		self.waitPoll(RA8875_ELLIPSE, RA8875_ELLIPSE_STATUS)

######################################################################
# Mid Level
######################################################################

	def GPIOX(self, on):
		if on:
			self.writeReg(RA8875_GPIOX, 1)
		else:
			self.writeReg(RA8875_GPIOX, 0)

######################################################################

######################################################################

	def PWM1out(self, p):
		self.writeReg(RA8875_P1DCR, p)

######################################################################

######################################################################
	
	def PWM2out(self, p):
		self.writeReg(RA8875_P2DCR, p)

######################################################################

######################################################################

	def PWM1config(self, on, clock):
		if on:
			self.writeReg(RA8875_P1CR, RA8875_P1CR_ENABLE | (clock & 0xF))
		else:
			self.writeReg(RA8875_P1CR, RA8875_P1CR_DISABLE | (clock & 0xF))

######################################################################

######################################################################

	def PWM2config(self, on, clock):
		if on:
			self.writeReg(RA8875_P2CR, RA8875_P2CR_ENABLE | (clock & 0xF))
		else:
			self.writeReg(RA8875_P2CR, RA8875_P2CR_DISABLE | (clock & 0xF))

######################################################################
# Enables or disables the on-chip touch screen controller
######################################################################

	def touchEnable(self, on):
		adcClk = RA8875_TPCR0_ADCCLK_DIV4

		if self._size == RA8875sizes.RA8875_800x480: # match up touch size with LCD size
			adcClk = RA8875_TPCR0_ADCCLK_DIV16

		if on:
			# /* Enable Touch Panel (Reg 0x70) */
			self.writeReg(RA8875_TPCR0, RA8875_TPCR0_ENABLE |
		                       RA8875_TPCR0_WAIT_4096CLK  |
		                       RA8875_TPCR0_WAKEENABLE   |
		                       adcClk) # 10mhz max!
			# /* Set Auto Mode      (Reg 0x71) */
			self.writeReg(RA8875_TPCR1, RA8875_TPCR1_AUTO    |
		                       # RA8875_TPCR1_VREFEXT |
		                       RA8875_TPCR1_DEBOUNCE)
			# /* Enable TP INT */
			self.writeReg(RA8875_INTC1, self.readReg(RA8875_INTC1) | RA8875_INTC1_TP)
		else:
			# /* Disable TP INT */
			self.writeReg(RA8875_INTC1, self.readReg(RA8875_INTC1) & ~RA8875_INTC1_TP)
			# /* Disable Touch Panel (Reg 0x70) */
			self.writeReg(RA8875_TPCR0, RA8875_TPCR0_DISABLE)

######################################################################
# Checks if a touch event has occured

# @returns  True is a touch event has occured (reading it via
#         touchRead() will clear the interrupt in memory)
######################################################################

	def touched(self):
		if (self.readReg(RA8875_INTC2) & RA8875_INTC2_TP):
			return True
		return False

######################################################################
# Reads the last touch event

# @args x[out]  Pointer to the uint16_t field to assign the raw X value
# @args y[out]  Pointer to the uint16_t field to assign the raw Y value

# @note Calling this function will clear the touch panel interrupt on
#     the RA8875, resetting the flag used by the 'touched' function
######################################################################

	def touchRead(self):
		tx = self.readReg(RA8875_TPXH)
		ty = self.readReg(RA8875_TPYH)
		temp = self.readReg(RA8875_TPXYL)
		tx <<= 2
		ty <<= 2
		tx |= temp & 0x03        # get the bottom x bits
		ty |= (temp >> 2) & 0x03 # get the bottom y bits

		# /* Clear TP INT Status */
		self.writeReg(RA8875_INTC2, RA8875_INTC2_TP)

		return {'x':tx,'y':ty}

######################################################################
# Turns the display on or off
######################################################################

	def displayOn(self, on):
		if on:
			self.writeReg(RA8875_PWRR, RA8875_PWRR_NORMAL | RA8875_PWRR_DISPON)
		else:
			self.writeReg(RA8875_PWRR, RA8875_PWRR_NORMAL | RA8875_PWRR_DISPOFF)

######################################################################
# Puts the display in sleep mode, or disables sleep mode if enabled
######################################################################
	
	def sleep(self, sleep):
		if sleep: 
			self.writeReg(RA8875_PWRR, RA8875_PWRR_DISPOFF | RA8875_PWRR_SLEEP)
		else:
			self.writeReg(RA8875_PWRR, RA8875_PWRR_DISPOFF)

######################################################################
# Low Level
######################################################################

	def writeReg(self, reg, val):
		self.writeCommand(reg)
		self.writeData(val)

######################################################################

######################################################################

	def readReg(self, reg):
		self.writeCommand(reg)
		return self.readData()
		# return 255

######################################################################

######################################################################

	def writeData(self, d):
		# try:
		# 	print 'writeData('+hex(d)+')'
		# except TypeError as e:
		# 	print 'writeData('+str(d)+')'
		# 	print e
		# digitalWrite(_cs, LOW);
		GPIO.output(self._cs, GPIO.LOW)
		# spi_begin();
		self.spi.xfer2([RA8875_DATAWRITE,d])
		# spi_end();
		# digitalWrite(_cs, HIGH);
		GPIO.output(self._cs, GPIO.HIGH)

######################################################################

######################################################################

	def readData(self):
		# digitalWrite(_cs, LOW);
		GPIO.output(self._cs, GPIO.LOW)
		# spi_begin();

		self.spi.xfer2([RA8875_DATAREAD])
		x = self.spi.readbytes(1)[0]
		# print 'readData(): '+str(x)
		# spi_end();

		# digitalWrite(_cs, HIGH);
		GPIO.output(self._cs, GPIO.HIGH)
		return x

######################################################################

######################################################################

	def writeCommand(self, d):
		# print 'writeCommand('+hex(d)+')'
		# digitalWrite(_cs, LOW);
		GPIO.output(self._cs, GPIO.LOW)
		# spi_begin();
		# self.spi.cshigh = False
		self.spi.xfer2([RA8875_CMDWRITE,d])
		# spi_end();

		# digitalWrite(_cs, HIGH);
		GPIO.output(self._cs, GPIO.HIGH)

######################################################################

######################################################################

	def readStatus(self):
		# digitalWrite(_cs, LOW);
		GPIO.output(self._cs, GPIO.LOW)
		# spi_begin();
		self.spi.xfer2([RA8875_CMDREAD])
		x = self.spi.readbytes(1)[0]
		# print 'readStatus(): '+str(x)
		# spi_end();

		# digitalWrite(_cs, HIGH);
		GPIO.output(self._cs, GPIO.HIGH)
		return x

######################################################################

######################################################################



