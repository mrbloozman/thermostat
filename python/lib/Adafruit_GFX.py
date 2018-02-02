# This is the core graphics library for all our displays, providing a common
# set of graphics primitives (points, lines, circles, etc.).  It needs to be
# paired with a hardware-specific library for each display device we carry
# (to handle the lower-level functions).

# Adafruit invests time and resources providing this open source code, please
# support Adafruit & open-source hardware by purchasing products from Adafruit!
 
# Copyright (c) 2013 Adafruit Industries.  All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from glcdfont import *

class GFX:
	def __init__(self,w,h):
		self.WIDTH = w
		self.HEIGHT = h
		self._width = self.WIDTH
		self._height = self.HEIGHT
		self.rotation = 0
		self.cursor_y = 0
		self.cursor_x = 0
		self.textsize = 1
		self.textcolor = 0xFFFF
		self.textbgcolor = 0xFFFF
		self.wrap = True

	# Draw a circle outline
	def drawCircle(self,x0,y0,r,color):
		f = 1 - r
		ddF_x = 1
		ddF_y = -2 * r
		x = 0
		y = r

		self.drawPixel(x0, y0+r, color)
		self.drawPixel(x0, y0-r, color)
		self.drawPixel(x0+r, y0, color)
		self.drawPixel(x0-r, y0, color)

		while (x<y):
			if f >= 0:
				y = y-1
				ddF_y = ddF_y+2
				f = f+ddF_y

			x=x+1
			ddF_x=ddF_x+2
			f = f+ddF_x

			self.drawPixel(x0 + x, y0 + y, color)
			self.drawPixel(x0 - x, y0 + y, color)
			self.drawPixel(x0 + x, y0 - y, color)
			self.drawPixel(x0 - x, y0 - y, color)
			self.drawPixel(x0 + y, y0 + x, color)
			self.drawPixel(x0 - y, y0 + x, color)
			self.drawPixel(x0 + y, y0 - x, color)
			self.drawPixel(x0 - y, y0 - x, color)

	def drawCircleHelper(self,x0,y0,r,cornername,color):
		f = 1-r
		ddF_x = 1
		ddF_y = -2*r
		x = 0
		y = r

		while (x<y):
			if f>=0:
				y = y-1
				ddF_y = ddF_y+2
				f = f+ddF_y

			x = x+1
			ddF_x = ddF_x+2
			f = f+ddF_x

			if (cornername & 0x4):
				self.drawPixel(x0 + x, y0 + y, color)
				self.drawPixel(x0 + y, y0 + x, color)
			if (cornername & 0x2):
				self.drawPixel(x0 + x, y0 - y, color)
				self.drawPixel(x0 + y, y0 - x, color)
			if (cornername & 0x8):
				self.drawPixel(x0 - y, y0 + x, color)
				self.drawPixel(x0 - x, y0 + y, color)
			if (cornername & 0x1):
				self.drawPixel(x0 - y, y0 - x, color)
				self.drawPixel(x0 - x, y0 - y, color)

	def fillCircle(self,x0,y0,r,color):
		self.drawFastVLine(x0,y0-r,2*r+1,color)
		self.fillCircleHelper(x0,y0,r,3,0,color)

	# Used to do circles and roundrects
	def fillCircleHelper(self,x0,y0,r,cornername,delta,color):
		f = 1-r
		ddF_x = 1
		ddF_y = -2*r
		x = 0
		y = r

		while (x<y):
			if (f>=0):
				y = y-1
				ddF_y = ddF_y+2
				f = f+ddF_y

			x = x+1
			ddF_x = ddF_x+2
			f = f+ddF_x

			if (cornername & 0x1):
				self.drawFastVLine(x0+x, y0-y, 2*y+1+delta, color)
				self.drawFastVLine(x0+y, y0-x, 2*x+1+delta, color)

			if (cornername & 0x2):
				self.drawFastVLine(x0-x, y0-y, 2*y+1+delta, color)
				self.drawFastVLine(x0-y, y0-x, 2*x+1+delta, color)

	# Bresenham's algorithm - thx wikpedia
	def drawLine(self,x0,y0,x1,y1,color):
		steep = abs(y1 - y0) > abs(x1 - x0)

		if steep:
			x0,y0 = y0,x0
			x1,y1 = y1,x1

		if (x0>x1):
			x0,x1 = x1,x0
			y0,y1 = y1,y0

		dx = x1 - x0
		dy = abs(y1 - y0)

		err = dx/2

		if (y0 < y1):
			ystep = 1
		else:
			ystep = -1

		for x0 in range(x0,x1):
			if (steep):
				self.drawPixel(y0, x0, color)
			else:
				self.drawPixel(x0, y0, color)
			err -= dy
			if (err < 0):
				y0 += ystep
				err += dx

	# Draw a rectangle
	def drawRect(self,x,y,w,h,color):
		self.drawFastHLine(x, y, w, color)
		self.drawFastHLine(x, y+h-1, w, color)
		self.drawFastVLine(x, y, h, color)
		self.drawFastVLine(x+w-1, y, h, color)

	def drawFastVLine(self,x,y,h,color):
		self.drawLine(x, y, x, y+h-1, color)

	def drawFastHLine(self,x,y,w,color):
		self.drawLine(x, y, x+w-1, y, color)

	def fillRect(self,x,y,w,h,color):
		for i in range(x,x+w):
			self.drawFastVLine(i, y, h, color)

	def fillScreen(self,color):
		self.fillRect(0, 0, self._width, self._height, color)

	# Draw a rounded rectangle
	def drawRoundRect(self,x,y,w,h,r,color):
		# smarter version
		self.drawFastHLine(x+r  , y    , w-2*r, color) # Top
		self.drawFastHLine(x+r  , y+h-1, w-2*r, color) # Bottom
		self.drawFastVLine(x    , y+r  , h-2*r, color) # Left
		self.drawFastVLine(x+w-1, y+r  , h-2*r, color) # Right
		# draw four corners
		self.drawCircleHelper(x+r    , y+r    , r, 1, color)
		self.drawCircleHelper(x+w-r-1, y+r    , r, 2, color)
		self.drawCircleHelper(x+w-r-1, y+h-r-1, r, 4, color)
		self.drawCircleHelper(x+r    , y+h-r-1, r, 8, color)

	# Fill a rounded rectangle
	def fillRoundRect(self, x, y, w, h, r, color):
		# smarter version
		self.fillRect(x+r, y, w-2*r, h, color)

		# draw four corners
		self.fillCircleHelper(x+w-r-1, y+r, r, 1, h-2*r-1, color)
		self.fillCircleHelper(x+r    , y+r, r, 2, h-2*r-1, color)

	# Draw a triangle
	def drawTriangle(self, x0, y0, x1, y1, x2, y2, color):
		self.drawLine(x0, y0, x1, y1, color)
		self.drawLine(x1, y1, x2, y2, color)
		self.drawLine(x2, y2, x0, y0, color)

	# Fill a triangle
	def fillTriangle(self, x0, y0, x1, y1, x2, y2, color):
		# Sort coordinates by Y order (y2 >= y1 >= y0)
		if (y0 > y1):
			y0,y1 = y1,y0 
			x0,x1 = x1,x0

		if (y1 > y2):
			y2,y1 = y1,y2
			x2,x1 = x1,x2

		if (y0 > y1):
			y0,y1 = y1,y0 
			x0,x1 = x1,x0

		if (y0 == y2): # Handle awkward all-on-same-line case as its own thing
			a = b = x0
			if (x1 < a):
				a = x1
			elif (x1 > b):
				b = x1
			if (x2 < a):
				a = x2
			elif (x2 > b):
				b = x2
			self.drawFastHLine(a, y0, b-a+1, color)
			return

		dx01 = x1 - x0
		dy01 = y1 - y0
		dx02 = x2 - x0
		dy02 = y2 - y0
		dx12 = x2 - x1
		dy12 = y2 - y1
		sa   = 0
		sb   = 0

		# For upper part of triangle, find scanline crossings for segments
		# 0-1 and 0-2.  If y1=y2 (flat-bottomed triangle), the scanline y1
		# is included here (and second loop will be skipped, avoiding a /0
		# error there), otherwise scanline y1 is skipped here and handled
		# in the second loop...which also avoids a /0 error here if y0=y1
		# (flat-topped triangle).
		if (y1 == y2):
			last = y1   # Include y1 scanline
		else:
			last = y1-1 # Skip it

		for y in range(y0,last):
			a   = x0 + sa / dy01
			b   = x0 + sb / dy02
			sa += dx01
			sb += dx02
			# /* longhand:
			# a = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
			# b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
			# */
			if (a > b):
				a,b = b,a
				self.drawFastHLine(a, y, b-a+1, color)

		# For lower part of triangle, find scanline crossings for segments
		# 0-2 and 1-2.  This loop is skipped if y1=y2.
		sa = dx12 * (y - y1)
		sb = dx02 * (y - y0)

		for y in range(y,y2):
			a   = x1 + sa / dy12
			b   = x0 + sb / dy02
			sa += dx12
			sb += dx02
			# /* longhand:
			# a = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
			# b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
			# */
			if (a > b):
				a,b = b,a
				self.drawFastHLine(a, y, b-a+1, color)

	def drawBitmap(self, x, y, bitmap, w, h, color):
		byteWidth = (w + 7) / 8

		for j in range(h):
			for i in range(w):
				if bitmap[(j * byteWidth + i / 8)] & (128 >> (i & 7)):
					self.drawPixel(x+i, y+j, color)

	def prnt(self,s):
		for i in range(len(s)):
			self.write(s[i])

	def prntln(self,s):
		self.prnt(s+'\n')

	def write(self,c):
		if (c == '\n'):
			self.cursor_y += self.textsize*8
			self.cursor_x  = 0
		elif (c == '\r'):
		# skip em
			pass
		else:
			self.drawChar(self.cursor_x, self.cursor_y, ord(c), self.textcolor, self.textbgcolor, self.textsize)
			self.cursor_x += self.textsize*6
			if (self.wrap and (self.cursor_x > (self._width - self.textsize*6))):
				self.cursor_y += self.textsize*8
				self.cursor_x = 0

	# Draw a character
	def drawChar(self, x, y, c, color, bg, size):
		if ((x >= self._width) | (y >= self._height) | ((x + 6 * size - 1) < 0) | ((y + 8 * size - 1) < 0)): # Clip
			return

		for i in range(6):
			if (i == 5):
				line = 0x0
			else:
				line = font[(c*5)+i]
			for j in range(8):
				if (line & 0x1):
					if (size == 1): # default size
						self.drawPixel(x+i, y+j, color)
					else:  # big size
						self.fillRect(x+(i*size), y+(j*size), size, size, color)
				elif (bg != color):
					if (size == 1): # default size
						self.drawPixel(x+i, y+j, bg)
					else : # big size
						self.fillRect(x+i*size, y+j*size, size, size, bg)
				line >>= 1

	def setCursor(self,x, y):
		self.cursor_x = x
		self.cursor_y = y

	def setTextSize(self, s):
		if (s>0):
			self.textsize = s
		else:
			self.textsize = 1

	# def setTextColor(self, c):
	# 	# For 'transparent' background, we'll set the bg 
	# 	# to the same as fg instead of using a flag
	# 	self.textcolor = self.textbgcolor = c

	def setTextColor(self, c, b):
		self.textcolor   = c
		self.textbgcolor = b 

	def setTextWrap(self, w):
		self.wrap = w

	def getRotation(self):
		return self.rotation

	def setRotation(self,x):
		self.rotation = (x & 3)
		
		if self.rotation == 0:
			pass
		if self.rotation == 2:
			self._width  = self.WIDTH
			self._height = self.HEIGHT
		if self.rotation == 1:
			pass
		if self.rotation == 3:
			self._width  = self.HEIGHT
			self._height = self.WIDTH

	# Return the size of the display (per current rotation)
	def width(self):
		return self._width

	def height(self):
		return self._height

	def invertDisplay(self, i):
		# Do nothing, must be subclassed if supported
		return