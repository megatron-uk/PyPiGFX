#!/usr/bin/env python3

import time
import sys

import settings
from utils import packetValid, packetUnwrap
from iodev import IoFifo, IoUsb, IoI2c, IoSpi
from sdlhelper import SDLDecoder, SDLEnvironment

exit = False

sdlenv = SDLEnvironment()
sdldecode = SDLDecoder(sdl_environment = sdlenv)


# Open connection
if settings.IO_MODE == "pipe":
	i = IoFifo()
if settings.IO_MODE == "usb":
	i = IoUsb()
if settings.IO_MODE == "i2c":
	i = IoI2c()
if settings.IO_MODE == "spi":
	i = IoSpi()

if (i.open()):
	print("%s: Info - Device opened" % (__name__))
else:
	print("%s: Error - Unable to open device" % (__name__))
	sys.exit(1)

print("%s: Starting listener loop" % (__name__))
while exit != True:
	# listen for incoming datastream
	data = i.read()
	if data is not None:
	
		# Unpack message	
		if packetValid(data):
			datastream = packetUnwrap(data)
			if datastream:
				# Map to SDL function call
				sdl_func_def = sdldecode.id_to_funcname(datastream)
				if sdl_func_def:
					print("%s: Valid datastream: %s" % (__name__, datastream))
					print("%s: Matched SDL function: %s" % (__name__, sdl_func_def))

				# Construct SDL function call
				f = sdldecode.construct_call(sdl_func_def, datastream)

				# Execute function call
				#sdldecode.execute_call(f)
		else:
			print("%s: Error - invalid data: %s" % (__name__, data))
