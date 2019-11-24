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
				
				result = sdldecode.result()
				
				# Map to SDL function call
				sdl_func = sdldecode.id_to_funcname(datastream)
				if sdl_func:
					# Construct SDL function call
					real_func,args = sdldecode.construct_call(sdl_func, datastream)
		
					# Execute function call
					if real_func:
						result = sdldecode.execute_call(sdl_func, real_func, args)
					
					# Encode result ready for transmission back to client
					new_datastream = sdldecode.encode_result(sdl_func, result)
					
				else:
					new_datastream = sdldecode.encode_result(None, result)
		else:
			print("%s: Error - invalid data: %s" % (__name__, data))
