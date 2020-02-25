#!/usr/bin/env python3

import time
import sys
from newlog import newlog
import settings
from utils import packetValid, packetUnwrap
from iodev import IoFifo, IoUsb, IoI2c, IoSpi, IoSerial
from sdlhelper import SDLDecoder, SDLEnvironment

logger = newlog(__name__)
exit = False

sdlenv = SDLEnvironment()
sdldecode = SDLDecoder(sdl_environment = sdlenv)


# Open connection
if settings.IO_MODE == "pipe":
	i = IoFifo()
if settings.IO_MODE == "serial":
	i = IoSerial()
if settings.IO_MODE == "usb":
	i = IoUsb()
if settings.IO_MODE == "i2c":
	i = IoI2c()
if settings.IO_MODE == "spi":
	i = IoSpi()

if (i.open()):
	logger.info("Device opened")
else:
	logger.fatal("Error - Unable to open device")
	sys.exit(1)

logger.info("Starting listener loop")
while exit != True:
	# listen for incoming datastream
	data = i.read()
	if data is not None:
	
		data_list = data.split('>')
		#logger.debug("DATALIST: %s" % data_list)
		for d in data_list[0:-1]:
			
			logger.debug("=====================")
			
			if d != '':
				d += '>'
	
			# Set default return objects
			result = sdldecode.result()
			new_datastream = sdldecode.encode_result(None, result)
			sdl_func = None
	
			# Unpack message	
			if packetValid(d):
				logger.debug("DATA: %s" % d)
				datastream = packetUnwrap(d)
				
				if datastream:				
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
				logger.warn("Error - invalid data: %s" % (d))
				new_datastream = sdldecode.encode_result(None, result)
		
			# Send return datastream with result	
			i.write(new_datastream)
			
		else:
			pass
			logger.debug("Warning - no data left in datastream")
