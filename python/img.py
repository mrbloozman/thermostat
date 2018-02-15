class NetPBM:
   def __init__(self):
      self._magicNumber = None
      self._comment = None
      self._width = None
      self._height = None
      self._maxColor = None
      self._src = []
      self._colorMap = []

   def load(self,filepath):
      with open(filepath,'rb') as f:
         for ln in f:
            if not self._magicNumber:
               if ln.replace('\n','') in ['P1','P2','P3','P4','P5','P6']:
                  self._magicNumber = ln.replace('\n','')
               else:
                  raise IOError('NetPBM: Could not determine magic number')
            elif ln[0]=='#':
               # print ln
               if not self._comment:
                  self._comment = ln
               else:
                  self._comment = self._comment + ln
            elif not self._width:
               props = ln.split()
               if len(props) >= 2:
                  self._width = int(props[0])
                  self._height = int(props[1])
               if len(props) == 3:
                  self._maxColor = int(props[2])
            elif not self._maxColor and self.maxColorRequired():
               props = ln.split()
               if len(props) == 1:
                  self._maxColor = int(props[0])
               else:
                  raise IOError('NetPBM: Could not find max color')
            elif self.isBitMap():
               self.srcBitMap(ln)
            elif self.isGrayMap():
               self.srcGrayMap(ln)

      self.validate()

   def srcBitMap(self,ln):
      if self._colorMap == []:
         self._colorMap = {0:0xffffff,1:0x000000}
      if self.isAscii():
         for px in ln.strip().split():
            if px in ['0','1']:
               self._src.append(int(px))
      elif self.isBinary():
         for px in ln.bytes():
            for i in range(8):
               self._src.append(px&(1<<i))

   def srcGrayMap(self,ln):
      if self._colorMap == []:
         self._colorMap = {0:0xffffff}
         self._colorMap[self._maxColor] = 0x000000
      if self.isAscii():
         for px in ln.strip().split():
            try:
               ipx = int(px)
               if ipx not in self._colorMap:
                  self._colorMap[ipx] = self.normalizeRGB(ipx,ipx,ipx)
               self._src.append(ipx)
            except ValueError as e:
               pass
      elif self.isBinary():
         for ipx in ln.bytes():
            if ipx not in self._colorMap:
               self._colorMap[ipx] = self.normalizeRGB(ipx,ipx,ipx)
            self._src.append(ipx)

   def normalizeRGB(self,r,g,b):
      return (self.normalizeColor(r)<<16)+(self.normalizeColor(g)<<8)+self.normalizeColor(b)

   def normalizeColor(self,c):
      return 255-int(255*c/self._maxColor)

   def validate(self):
      if (self._width * self._height) != len(self._src):
         raise IOError('NetPBM: Load is not valid')
                  

   def maxColorRequired(self):
      if self._magicNumber in ['P2','P3','P5','P6']:
         return True
      else:
         return False

   def isAscii(self):
      if self._magicNumber in ['P1','P2','P3']:
         return True
      else:
         return False

   def isBinary(self):
      if self._magicNumber in ['P4','P5','P6']:
         return True
      else:
         return False

   def isBitMap(self):
      if self._magicNumber in ['P1','P4']:
         return True
      else:
         return False

   def isGrayMap(self):
      if self._magicNumber in ['P2','P5']:
         return True
      else:
         return False

   def isPixMap(self):
      if self._magicNumber in ['P3','P6']:
         return True
      else:
         return False

img = NetPBM()
img.load('static/img/example.pgm')
print vars(img)

fan3=[0x00, 0x3c, 0x00, 0x00, 0x80, 0x7f, 0x00, 0x00, 0xe0, 0xff, 0x00, 0x00,
   0xf0, 0xff, 0xe0, 0x07, 0xf0, 0xff, 0xf0, 0x1f, 0xf8, 0xff, 0xf8, 0x3f,
   0xf8, 0x7f, 0xfc, 0x3f, 0xf8, 0x7f, 0xfc, 0x7f, 0xf8, 0x7f, 0xfc, 0x7f,
   0xf8, 0x7f, 0xfe, 0x7f, 0xf8, 0x7f, 0xfe, 0xff, 0xf0, 0x7f, 0xfe, 0xff,
   0xe0, 0x7f, 0xff, 0xff, 0xc0, 0xff, 0xff, 0xff, 0x00, 0x7e, 0xff, 0x7f,
   0x00, 0x70, 0x06, 0x3c, 0x3c, 0x20, 0x0c, 0x00, 0xfe, 0x7f, 0x7f, 0x00,
   0xff, 0xff, 0xff, 0x03, 0xff, 0xff, 0xfe, 0x07, 0xff, 0x7f, 0xfe, 0x0f,
   0xff, 0x7f, 0xfe, 0x1f, 0xfe, 0x7f, 0xfe, 0x1f, 0xfe, 0x3f, 0xfe, 0x1f,
   0xfe, 0x3f, 0xfe, 0x1f, 0xfc, 0x3f, 0xfe, 0x1f, 0xfc, 0x1f, 0xff, 0x1f,
   0xf8, 0x0f, 0xff, 0x0f, 0xe0, 0x07, 0xff, 0x0f, 0x00, 0x00, 0xff, 0x07,
   0x00, 0x00, 0xfe, 0x01, 0x00, 0x00, 0x3c, 0x00]

fan2=[0x00, 0xfc, 0x1f, 0x00, 0x00, 0xfe, 0x3f, 0x00, 0x00, 0xfe, 0x7f, 0x00,
   0x00, 0xff, 0x3f, 0x00, 0x00, 0xff, 0x7f, 0x00, 0x00, 0xff, 0x3f, 0x00,
   0x00, 0xff, 0x1f, 0x00, 0x00, 0xff, 0x0f, 0x00, 0x00, 0xfe, 0x07, 0x1f,
   0x14, 0xfe, 0xc7, 0x7f, 0x3e, 0xfc, 0xe3, 0xff, 0x7f, 0xf8, 0xf1, 0xff,
   0xff, 0xf0, 0xf9, 0xff, 0xff, 0xe3, 0xff, 0xff, 0xff, 0xe7, 0xfe, 0xff,
   0xff, 0x7f, 0xfe, 0xff, 0xff, 0x7f, 0xfe, 0xff, 0xff, 0x7f, 0xe7, 0xff,
   0xff, 0xdf, 0xc3, 0xff, 0xff, 0x9f, 0x0f, 0xff, 0xff, 0x8f, 0x1f, 0xfe,
   0xff, 0xc7, 0x3f, 0x7c, 0xfe, 0xe3, 0x7f, 0x28, 0xf8, 0xe0, 0x7f, 0x00,
   0x00, 0xf0, 0xff, 0x00, 0x00, 0xf8, 0xff, 0x00, 0x00, 0xfc, 0xff, 0x00,
   0x00, 0xfe, 0xff, 0x00, 0x00, 0xfc, 0xff, 0x00, 0x00, 0xfe, 0x7f, 0x00,
   0x00, 0xfc, 0x7f, 0x00, 0x00, 0xf8, 0x3f, 0x00]

fan1=[0x00, 0x00, 0x7e, 0x00, 0x00, 0x80, 0xff, 0x01, 0x00, 0xc0, 0xff, 0x03,
   0x00, 0xc0, 0xff, 0x07, 0xf0, 0xc1, 0xff, 0x0f, 0xf8, 0xe3, 0xff, 0x0f,
   0xfc, 0xe7, 0xff, 0x0f, 0xfe, 0xe7, 0xff, 0x0f, 0xfe, 0xc7, 0xff, 0x0f,
   0xff, 0xe7, 0xff, 0x07, 0xff, 0xcf, 0xff, 0x03, 0xff, 0x8f, 0x3f, 0x00,
   0xff, 0x9f, 0x0f, 0x00, 0xff, 0xdf, 0x43, 0x07, 0xff, 0xff, 0xef, 0x3f,
   0xfe, 0x7f, 0xfc, 0x7f, 0xfe, 0x7f, 0xfe, 0x7f, 0xfc, 0xe7, 0xff, 0xff,
   0xe0, 0xc2, 0xfb, 0xff, 0x00, 0xf0, 0xfb, 0xff, 0x00, 0xfc, 0xf1, 0xff,
   0xc0, 0xff, 0xf3, 0xff, 0xe0, 0xff, 0xe7, 0xff, 0xf0, 0xff, 0xe3, 0x7f,
   0xf0, 0xff, 0xe7, 0x7f, 0xf0, 0xff, 0xe7, 0x3f, 0xf0, 0xff, 0xc7, 0x1f,
   0xf0, 0xff, 0x83, 0x0f, 0xe0, 0xff, 0x03, 0x00, 0xc0, 0xff, 0x03, 0x00,
   0x80, 0xff, 0x01, 0x00, 0x00, 0x7e, 0x00, 0x00]

flame1=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00,
   0x00, 0xc0, 0x00, 0x00, 0x00, 0xc0, 0x01, 0x00, 0x00, 0xc0, 0x03, 0x00,
   0x00, 0xc0, 0x03, 0x00, 0x00, 0xc0, 0x07, 0x00, 0x00, 0xc0, 0x07, 0x00,
   0x00, 0xe0, 0x87, 0x00, 0x00, 0xf0, 0xe7, 0x00, 0x00, 0xf8, 0xe3, 0x00,
   0x00, 0xfe, 0xe3, 0x00, 0x00, 0xff, 0xe1, 0x00, 0x80, 0xff, 0xe0, 0x01,
   0xc0, 0xff, 0xe0, 0x03, 0xe0, 0xff, 0xf1, 0x03, 0xe0, 0xff, 0xff, 0x07,
   0xf0, 0xf7, 0xff, 0x07, 0xf0, 0xf7, 0xff, 0x07, 0xf0, 0xf3, 0xff, 0x07,
   0xf0, 0xf1, 0xff, 0x07, 0xf0, 0xf1, 0xff, 0x03, 0xf0, 0xe1, 0xfc, 0x03,
   0xf0, 0x01, 0xf8, 0x03, 0xe0, 0x01, 0xf0, 0x01, 0xe0, 0x01, 0xf0, 0x00,
   0xc0, 0x01, 0x70, 0x00, 0x80, 0x03, 0x38, 0x00, 0x00, 0x06, 0x08, 0x00,
   0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

flame2=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
   0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x03, 0x00,
   0x00, 0x80, 0x03, 0x00, 0x00, 0x84, 0x83, 0x00, 0x00, 0xc4, 0x87, 0x00,
   0x00, 0xc6, 0x87, 0x00, 0x00, 0xe2, 0x87, 0x01, 0x00, 0xe3, 0x8f, 0x01,
   0x00, 0xf3, 0x8f, 0x03, 0x80, 0xf3, 0x9f, 0x03, 0xc0, 0xf9, 0x1f, 0x07,
   0xe0, 0xf9, 0x3f, 0x0f, 0xf0, 0xf9, 0x3f, 0x0f, 0xf0, 0xfc, 0x3f, 0x1e,
   0xf8, 0xfc, 0x7f, 0x1e, 0xf8, 0xfc, 0x47, 0x1e, 0xf8, 0xfc, 0x01, 0x1e,
   0xf8, 0xf8, 0x01, 0x1e, 0xf8, 0xf9, 0x01, 0x1f, 0xf8, 0xf3, 0x81, 0x1f,
   0xf8, 0xff, 0xe7, 0x1f, 0xf8, 0xff, 0xff, 0x1f, 0xf0, 0xff, 0xff, 0x0f,
   0xe0, 0xff, 0xff, 0x07, 0xe0, 0xff, 0xff, 0x03, 0x80, 0xff, 0xff, 0x01,
   0x00, 0xff, 0xff, 0x00, 0x00, 0xfc, 0x3f, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00]

flame3=[0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x01, 0x00, 0x00, 0x80, 0x01, 0x00,
   0x00, 0x80, 0x01, 0x00, 0x00, 0xc0, 0x03, 0x00, 0x00, 0xc0, 0x03, 0x00,
   0x00, 0xe0, 0x07, 0x00, 0x00, 0xf0, 0x07, 0x00, 0x00, 0xf0, 0x0f, 0x00,
   0x00, 0xf8, 0x1f, 0x00, 0x00, 0xfc, 0x3f, 0x00, 0x00, 0xfe, 0x7f, 0x00,
   0x00, 0xfe, 0x7f, 0x00, 0x00, 0xff, 0xff, 0x00, 0x80, 0xff, 0xff, 0x01,
   0x80, 0xff, 0xff, 0x01, 0xc0, 0x7f, 0xfe, 0x03, 0xc0, 0x7f, 0xfe, 0x03,
   0xc0, 0x3f, 0xfc, 0x03, 0xe0, 0x1f, 0xf8, 0x07, 0xe0, 0x0f, 0xf0, 0x07,
   0xe0, 0x0f, 0xf0, 0x07, 0xe0, 0x07, 0xe0, 0x07, 0xe0, 0x03, 0xc0, 0x07,
   0xe0, 0x03, 0xc0, 0x07, 0xc0, 0x03, 0xc0, 0x03, 0xc0, 0x03, 0xc0, 0x03,
   0x80, 0x03, 0xc0, 0x03, 0x80, 0x03, 0xc0, 0x01, 0x00, 0x03, 0xc0, 0x00,
   0x00, 0x06, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00]

flake1=[0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x04, 0x00, 0x00, 0x31, 0x8c, 0x00,
   0x00, 0x33, 0xcc, 0x00, 0x00, 0x1b, 0xd8, 0x00, 0x00, 0x1e, 0x78, 0x00,
   0xe0, 0x0f, 0xf0, 0x07, 0xe0, 0x4f, 0xf2, 0x07, 0x00, 0x78, 0x1e, 0x00,
   0x00, 0x78, 0x1e, 0x00, 0x00, 0x7e, 0x7e, 0x00, 0x0c, 0x7c, 0x3e, 0x30,
   0x1c, 0x79, 0x9e, 0x38, 0x98, 0xe3, 0xc7, 0x19, 0x30, 0xcf, 0xf3, 0x0c,
   0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x30, 0xcf, 0xf3, 0x0c,
   0x98, 0xe3, 0xc7, 0x19, 0x1c, 0x79, 0x9e, 0x38, 0x0c, 0x7e, 0x7e, 0x30,
   0x00, 0x7e, 0x7e, 0x00, 0x00, 0x78, 0x1e, 0x00, 0x00, 0x78, 0x1e, 0x00,
   0xe0, 0x4f, 0xf2, 0x07, 0xe0, 0x0f, 0xf0, 0x07, 0x00, 0x1e, 0x78, 0x00,
   0x00, 0x1b, 0xd8, 0x00, 0x00, 0x33, 0xcc, 0x00, 0x00, 0x31, 0x8c, 0x00,
   0x00, 0x20, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00]

flake2=[0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0x60, 0x0c, 0x00,
   0x00, 0x60, 0x07, 0x00, 0x00, 0xfe, 0x83, 0x01, 0x00, 0xfc, 0x81, 0x01,
   0x00, 0xe0, 0x80, 0x19, 0x60, 0xc0, 0x80, 0x1d, 0x60, 0xc0, 0x86, 0x0f,
   0x60, 0xf0, 0xb3, 0x07, 0x64, 0xf0, 0xfb, 0x1f, 0x7e, 0xe6, 0xf9, 0x3c,
   0xfc, 0xcc, 0x79, 0x20, 0xf0, 0x9f, 0xf9, 0x01, 0x38, 0xbf, 0xff, 0x00,
   0x1c, 0xff, 0x07, 0x00, 0x0c, 0xef, 0xc7, 0x61, 0x00, 0xc0, 0xff, 0x71,
   0x00, 0xfe, 0xfb, 0x39, 0x00, 0x7f, 0xf3, 0x1f, 0x08, 0x3c, 0x67, 0x3f,
   0x38, 0x3e, 0xcf, 0xfc, 0xf8, 0xb7, 0x1f, 0x4c, 0xc0, 0x9b, 0x1f, 0x0c,
   0xe0, 0xc3, 0x06, 0x0c, 0x70, 0x03, 0x06, 0x0c, 0x30, 0x03, 0x0e, 0x00,
   0x00, 0x03, 0x7f, 0x00, 0x00, 0x83, 0xff, 0x00, 0x00, 0xc0, 0x8d, 0x00,
   0x00, 0xe0, 0x0c, 0x00, 0x00, 0x00, 0x0c, 0x00]

flake3=[0x00, 0x00, 0x06, 0x00, 0x00, 0x20, 0x06, 0x00, 0x00, 0xe0, 0x06, 0x00,
   0x00, 0xc1, 0x7f, 0x00, 0x80, 0x81, 0x3f, 0x00, 0x98, 0x01, 0x0f, 0x00,
   0xb8, 0x01, 0x03, 0x06, 0xf0, 0x61, 0x03, 0x06, 0xe0, 0xcd, 0x0f, 0x06,
   0xf8, 0xdf, 0x0f, 0x26, 0x3c, 0x9f, 0x67, 0x7e, 0x04, 0x9e, 0x33, 0x1f,
   0x80, 0xbf, 0xf9, 0x0f, 0x00, 0xff, 0xfd, 0x1c, 0x00, 0xe0, 0xff, 0x38,
   0x86, 0xe7, 0xf3, 0x30, 0x8e, 0xff, 0x03, 0x00, 0x9c, 0xdf, 0x7f, 0x00,
   0xf8, 0xcf, 0xfe, 0x00, 0x7c, 0xe6, 0x3c, 0x10, 0x3e, 0xf3, 0x7c, 0x1e,
   0x32, 0xf8, 0xfd, 0x0f, 0x30, 0xf8, 0xd9, 0x03, 0x30, 0x60, 0xc3, 0x07,
   0x30, 0x60, 0xc0, 0x0e, 0x00, 0x70, 0xc0, 0x0c, 0x00, 0xfe, 0xc0, 0x00,
   0x00, 0xff, 0x41, 0x00, 0x00, 0xb0, 0x03, 0x00, 0x00, 0x30, 0x06, 0x00,
   0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

jedi=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0xf8, 0x1f, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00,
   0x00, 0xc0, 0xff, 0xff, 0x03, 0x00, 0x00, 0xf0, 0x03, 0xc0, 0x0f, 0x00,
   0x00, 0xf8, 0x00, 0x00, 0x1f, 0x00, 0x00, 0x3e, 0x00, 0x00, 0x7c, 0x00,
   0x00, 0x0f, 0x00, 0x00, 0xf0, 0x00, 0x80, 0x07, 0x00, 0x00, 0xe0, 0x01,
   0x80, 0x43, 0x00, 0x00, 0xc2, 0x01, 0xc0, 0x21, 0x00, 0x00, 0x84, 0x03,
   0xe0, 0x30, 0x00, 0x00, 0x0c, 0x07, 0xe0, 0x30, 0x00, 0x00, 0x0c, 0x07,
   0x70, 0x38, 0x00, 0x00, 0x1c, 0x0e, 0x70, 0x38, 0x00, 0x00, 0x1c, 0x0e,
   0x38, 0x7c, 0x00, 0x00, 0x3e, 0x1c, 0x38, 0x7c, 0x00, 0x00, 0x3e, 0x1c,
   0x18, 0xfc, 0x00, 0x00, 0x3f, 0x18, 0x1c, 0xfc, 0x00, 0x00, 0x3f, 0x38,
   0x9c, 0xfd, 0x01, 0x80, 0xbf, 0x39, 0x9c, 0xfd, 0x01, 0x80, 0xbf, 0x39,
   0x9c, 0xfd, 0x03, 0xc0, 0xbf, 0x39, 0x9c, 0xfd, 0x81, 0x81, 0xbf, 0x39,
   0x9c, 0xfb, 0x81, 0x81, 0xdf, 0x39, 0x9c, 0xfb, 0x81, 0x81, 0xdf, 0x39,
   0x9c, 0xff, 0x80, 0x01, 0xff, 0x39, 0x1c, 0xff, 0x80, 0x01, 0xff, 0x38,
   0x1c, 0xff, 0x80, 0x01, 0xff, 0x38, 0x18, 0xff, 0xc0, 0x03, 0xff, 0x18,
   0x38, 0xff, 0xc0, 0x03, 0xff, 0x1c, 0x38, 0xff, 0xf0, 0x0f, 0xff, 0x1c,
   0x70, 0xfe, 0xc1, 0x83, 0x7f, 0x0e, 0x70, 0xfe, 0xc1, 0x83, 0x7f, 0x0e,
   0xe0, 0xfc, 0xa1, 0x85, 0x3f, 0x07, 0xe0, 0xfc, 0x83, 0xc1, 0x3f, 0x07,
   0xc0, 0xf9, 0x87, 0xe1, 0x9f, 0x03, 0x80, 0xf3, 0x8f, 0xf1, 0xcf, 0x01,
   0x80, 0xc7, 0x9f, 0xf9, 0xe3, 0x01, 0x00, 0x8f, 0xff, 0xff, 0xf1, 0x00,
   0x00, 0x3e, 0xfc, 0x3f, 0x7c, 0x00, 0x00, 0xf8, 0x00, 0x00, 0x1f, 0x00,
   0x00, 0xf0, 0x03, 0xc0, 0x0f, 0x00, 0x00, 0xc0, 0xff, 0xff, 0x03, 0x00,
   0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xf8, 0x1f, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

makey=[0x00, 0x00, 0xe0, 0x07, 0x00, 0x00, 0x00, 0x00, 0xf8, 0x1f, 0x00, 0x00,
   0x00, 0x00, 0xfe, 0x7f, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00,
   0x00, 0x80, 0xff, 0xff, 0x01, 0x00, 0x00, 0x80, 0xf0, 0x0f, 0x01, 0x00,
   0x00, 0xc0, 0xf0, 0x0f, 0x03, 0x00, 0x00, 0xc0, 0xf0, 0x0f, 0x03, 0x00,
   0x00, 0xc0, 0xf0, 0x0f, 0x03, 0x00, 0x00, 0xe0, 0xfb, 0xdf, 0x07, 0x00,
   0x00, 0xe0, 0xff, 0xff, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xf0, 0xff, 0xff, 0x0f, 0x00, 0x00, 0xf8, 0xff, 0xff, 0x0f, 0x00,
   0x00, 0xf8, 0xff, 0xfe, 0x1f, 0x00, 0xe0, 0xfb, 0x1f, 0xf8, 0xdf, 0x07,
   0xf8, 0xfb, 0x07, 0xe0, 0xdf, 0x0f, 0xfc, 0xfb, 0x3b, 0xdc, 0xdf, 0x3f,
   0xfc, 0xfb, 0x3b, 0xdc, 0xdf, 0x3f, 0xfe, 0xfb, 0x79, 0x9e, 0xdf, 0x7f,
   0xfe, 0xfb, 0x79, 0x9e, 0xdf, 0x7f, 0xff, 0xfb, 0x59, 0x9a, 0xdf, 0xff,
   0xff, 0xfb, 0xd9, 0x9a, 0xdf, 0xff, 0xff, 0xfb, 0xd9, 0x9b, 0xdf, 0xff,
   0xff, 0xfb, 0xdb, 0xd9, 0xdf, 0xff, 0xff, 0xfb, 0x9b, 0xd9, 0xdf, 0xff,
   0xf8, 0xf8, 0x07, 0xe1, 0x1f, 0x1f, 0xf8, 0xf8, 0x0f, 0xf0, 0x1f, 0x1f,
   0xfc, 0xf8, 0x3f, 0xfc, 0x1f, 0x3f, 0xfc, 0xf9, 0xff, 0xff, 0x9f, 0x3f,
   0xfc, 0xf1, 0xff, 0xff, 0x8f, 0x3f, 0xfc, 0xe1, 0xff, 0xff, 0x87, 0x3f,
   0xfe, 0xc1, 0x1f, 0xf8, 0x83, 0x7f, 0xfe, 0xc1, 0x1f, 0xf8, 0x83, 0x7f,
   0xfe, 0xe1, 0x1f, 0xf8, 0x83, 0x7f, 0xfe, 0xe3, 0x1f, 0xf8, 0xc3, 0x7f,
   0xfe, 0xe3, 0x1f, 0xf8, 0xc3, 0x7f, 0xfe, 0xc3, 0x1f, 0xf8, 0xc3, 0x7f,
   0x00, 0xe0, 0x1f, 0x00, 0x00, 0x00, 0xfe, 0xf3, 0x1f, 0xf8, 0xcf, 0x7f,
   0xfc, 0xf3, 0x1f, 0xf8, 0xcf, 0x3f, 0xfc, 0xf3, 0x1f, 0xf8, 0xcf, 0x3f,
   0xf8, 0xf3, 0x1f, 0xf8, 0xcf, 0x1f, 0xe0, 0xfb, 0x1f, 0xfc, 0xcf, 0x07,
   0x00, 0xf8, 0x3f, 0xfc, 0x1f, 0x00, 0x00, 0xf8, 0x3f, 0xfc, 0x1f, 0x00,
   0x00, 0xf8, 0x3f, 0xfc, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xfe, 0x3f, 0xfc, 0x7f, 0x00, 0x00, 0xff, 0x3f, 0xfc, 0x7f, 0x00,
   0x00, 0xff, 0x3f, 0xfc, 0xff, 0x00]

def bitSwap(b):
	x = 0b00000000
	for i in range(8):
		if (b&(1<<i)):
			x+=(128>>i)
	return x

def bitSwapList(l):
	i=0
	for f in l:
		newpic=[]
		for b in f:
			newpic.append(bitSwap(b))
		l[i]=newpic
		i+=1
	return l