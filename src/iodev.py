#!/usr/bin/env python3

import time
import sys
import os
import settings
from newlog import newlog

logger = newlog(__name__)
class Io():
	""" Generic IO read/write function """
	def __init__(self):
		self.debug = settings.DEBUG
		self.device = None

	def read(self):
		try:
			reread = True
			datastream = ""
			m = 0
			start = time.time()
			while reread is True:
				m += 1
				d = self.device['in'].read(1)
				if d is not None:
					datastream += d
				if d == '>':
					reread = False
				if time.time() > start + settings.TIMEOUT:
					reread = False
			if datastream == '':
				return None
			return datastream
		except Exception as e:
			#logger.warn("Warning whilst reading from device")
			#logger.warn("Warning was: %s" % e)
			return None

	def write(self, data):
		try:
			returncode = self.device['out'].write(data)
			self.device['out'].flush()
			logger.debug("Wrote %s bytes to %s" % (returncode, self.device['out']))
			return returncode
		except Exception as e:
			logger.error("Error writing to device")
			logger.error("Error was: %s" % (e))
			self.close()
			self.open()	
			return False

class IoFifo(Io):
	""" Specific IO function for a unix FIFO """

	def __init__(self):
		super().__init__()
	
	def open(self, write_fifo = settings.FIFO_CLIENT_NAME, read_fifo = settings.FIFO_MASTER_NAME, write_destroy = True):
		""" Open a unix file as a pipe """
		try:
			# We only create our own input pipe
			# its up to the other process to create 
			# the output
			if not os.path.exists(read_fifo):
				logger.debug("Creating %s" % (read_fifo))
				os.mkfifo(read_fifo)

			logger.debug("Opening input pipe %s" % (read_fifo))
			fd1 = os.open(read_fifo, os.O_RDWR | os.O_NONBLOCK)
			f1 = os.fdopen(fd1, 'r')

			logger.debug("Opening output pipe %s" % (write_fifo))
			connected = False
			while connected == False:
				try:
					logger.info("Waiting for output pipe")
					fd2 = os.open(write_fifo, os.O_WRONLY | os.O_NONBLOCK)
					f2 = os.fdopen(fd2, 'w')
					connected = True
				except Exception as e:
					logger.error("Error: %s" % (e))
					time.sleep(3)

			self.device = {
				'in' : f1,
				'out' : f2,
			}
			logger.debug("Device: %s" % (self.device))
			return True
		except Exception as e:
			logger.error("Error while creating FIFO")
			logger.error("Error was: %s" % (e))
			return False

	def close(self):
		""" Close a file """
		try:
			if self.device['in']:
				close(self.device['in'])
			if self.device['out']:
				close(self.device['out'])
			self.device = None
			return True
		except Exception as e:
			logger.error("Error while closing FIFO")
			logger.error("Error was: %s" % (e))
			return False

class IoUsb(Io):

	def __init__(self):
		super().__init__()

	def open(self):
		""" Open a USB serial device """
		pass

	def close(self):
		""" Close a USB serial device """
		pass

class IoI2c(Io):
	
	def __init__(self):
		super().__init__()

	def open(self):
		""" Open a I2C interface """
		pass
		
	def close(self):
		""" Close an I2C interface """
		pass

class IoSpi(Io):

	def __init__(self):
		super().__init__(self)

	def open(self):
		""" Open an SPI connection """
		pass

	def close(self):
		""" Close an SPI connection """
		pass

def fifoclient(instructions = []):
	""" A basic client to send datastreams to a listening master process """

	logger.info("Starting FIFO client...")
	i = IoFifo()
	if (i.open(read_fifo = settings.FIFO_CLIENT_NAME, write_fifo = settings.FIFO_MASTER_NAME)):
		logger.info("Opened FIFO")
	else:
		logger.fatal("Unable to open FIFO")
		sys.exit(1)

	for ci in range(0,100):
		i.read()

		
	do_SDL_Init = "<01(32)>"
	do_SDL_CreateWindow = "<03(Test,0,0,640,480,0)>"
	do_SDL_CreateRenderer = "<04(1,0,0,0)>"
	do_SDL_CreateRGBSurface = "<05(0,640,480,24,0,0,0,255)>"
	do_SDL_MapRGB = "<06(3,255,0,0)>"
	do_SDL_FillRect = "<07(3,,16711680)>"

	i.write(do_SDL_Init)
	datastream = None
	while datastream is None:
		datastream = i.read()
	logger.debug("%s" % datastream)
	i.write(do_SDL_CreateWindow)
	datastream = None
	while datastream is None:
		datastream = i.read()
	logger.debug("%s" % datastream)
	i.write(do_SDL_CreateRenderer)
	datastream = None
	while datastream is None:
		datastream = i.read()
	logger.debug("%s" % datastream)
	i.write(do_SDL_CreateRGBSurface)
	datastream = None
	while datastream is None:
		datastream = i.read()
	logger.debug("%s" % datastream)
	i.write(do_SDL_MapRGB)
	datastream = None
	while datastream is None:
		datastream = i.read()
	logger.debug("%s" % datastream)
	i.write(do_SDL_FillRect)
	datastream = None
	while datastream is None:
		datastream = i.read()
	logger.debug("%s" % datastream)
	while True:
		logger.info("Enter data:")
		dataout = input()
		s = i.write(dataout)
		logger.info("Checking for response...")
		datastream = None
		while datastream is None:
			datastream = i.read()
		logger.info("Response: %s" % datastream)
		
