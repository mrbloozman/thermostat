# Methods
# -------

# open(bus, device)

# Connects to the specified SPI device, opening /dev/spidev-bus.device

# readbytes(n)

# Read n bytes from SPI device.

# writebytes(list of values)

# Writes a list of values to SPI device.

# xfer(list of values[, speed_hz, delay_usec, bits_per_word])

# Performs an SPI transaction. Chip-select should be released and reactivated between blocks.
# Delay specifies the delay in usec between blocks.

# xfer2(list of values[, speed_hz, delay_usec, bits_per_word])

# Performs an SPI transaction. Chip-select should be held active between blocks.

# close()

# Disconnects from the SPI device.

import CHIP_IO.OverlayManager as OM
import CHIP_IO.GPIO as GPIO
# import spidev
import time
import sys
sys.path.append('lib')
from Adafruit_RA8875 import *
# OM.toggle_debug()
# GPIO.setup('XIO-P3',GPIO.OUT)
# GPIO.output('XIO-P3',GPIO.LOW)
# time.sleep(0.1)
# GPIO.output('XIO-P3',GPIO.HIGH)
# time.sleep(0.1)

# OM.load("CUST","overlays/sample-spi.dtbo")
# OM.get_custom_loaded()

OM.load('SPI2')
# # print OM.get_spi_loaded()
# spi = spidev.SpiDev()
# spi.open(32766,0)
# spi.max_speed_hz = 500000
# spi.mode = 0b01

# to_send = [RA8875_CMDWRITE, RA8875_PWRR]
# spi.xfer2(to_send)
# to_send = [RA8875_DATAWRITE, RA8875_PWRR_NORMAL | RA8875_PWRR_DISPON]
# spi.xfer2(to_send)


lcd = Adafruit_RA8875('XIO-P2','XIO-P3')
if lcd.begin(RA8875sizes.RA8875_800x480):
	print 'lcd initialized'
	lcd.displayOn(True)
	print 'displayOn complete'
	lcd.fillScreen(RA8875_WHITE)
	print 'fillScreen complete'

