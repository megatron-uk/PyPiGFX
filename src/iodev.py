#!/usr/bin/env python3

import time
import sys
import os
import settings

class Io():

	def __init__(self):
		self.debug = settings.DEBUG
		self.device = None

	def open(self):
		pass

	def read(self):
		try:
			datastream = self.device['in'].read()
			return datastream
		except Exception as e:
			#print("Error reading from device")
			#print("Error was: %s" % e)
			return None

	def write(self, data):
		try:
			returncode = self.device['out'].write(data)
			self.device['out'].flush()
			if self.debug:
				print("%s : Wrote %s bytes to %s" % (__class__.__name__, returncode, self.device['out']))
			return returncode
		except Exception as e:
			print("%s : Error writing to device" % (__class__.__name__))
			print("%s : Error was: %s" % (__class__.__name__, e))
			return False

	def close(self):
		pass

class IoFifo(Io):

	def __init__(self):
		super().__init__()
	
	def open(self, write_fifo = settings.FIFO_CLIENT_NAME, read_fifo = settings.FIFO_MASTER_NAME, write_destroy = True):
		""" Open a unix file as a pipe """
		try:
			# We only create our own input pipe
			# its up to the other process to create 
			# the output
			if not os.path.exists(read_fifo):
				print("%s: Creating %s" % (__class__.__name__, read_fifo))
				os.mkfifo(read_fifo)

			print("%s: Opening input pipe %s" % (__class__.__name__, read_fifo))
			fd1 = os.open(read_fifo, os.O_RDWR | os.O_NONBLOCK)
			f1 = os.fdopen(fd1, 'r')

			print("%s: Opening output pipe %s" % (__class__.__name__, write_fifo))
			connected = False
			while connected == False:
				try:
					print("%s: Waiting for output pipe" % (__class__.__name__))
					fd2 = os.open(write_fifo, os.O_WRONLY | os.O_NONBLOCK)
					f2 = os.fdopen(fd2, 'w')
					connected = True
				except Exception as e:
					print("%s: Error: %s" % (__class__.__name__, e))
					time.sleep(3)

			self.device = {
				'in' : f1,
				'out' : f2,
			}
			if self.debug:
				print("%s: Device: %s" % (__class__.__name__, self.device))
			return True
		except Exception as e:
			print("%s: Error while creating FIFO" % (__class__.__name__))
			print("%s: Error was: %s" % (__class__.__name__, e))
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
			print("%s: Error while closing FIFO" % (__class__.__name__))
			print("%s: Error was: %s" % (__class__.__name__, e))
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

	print("%s: Starting FIFO client..." % (__name__))
	i = IoFifo()
	if (i.open(read_fifo = settings.FIFO_CLIENT_NAME, write_fifo = settings.FIFO_MASTER_NAME)):
		print("%s: Opened FIFO" % (__name__))
	else:
		print("%s: Unable to open FIFO" % (__name__))
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
	print("%s" % datastream)
	i.write(do_SDL_CreateWindow)
	datastream = None
	while datastream is None:
		datastream = i.read()
	print("%s" % datastream)
	i.write(do_SDL_CreateRenderer)
	datastream = None
	while datastream is None:
		datastream = i.read()
	print("%s" % datastream)
	i.write(do_SDL_CreateRGBSurface)
	datastream = None
	while datastream is None:
		datastream = i.read()
	print("%s" % datastream)
	i.write(do_SDL_MapRGB)
	datastream = None
	while datastream is None:
		datastream = i.read()
	print("%s" % datastream)
	i.write(do_SDL_FillRect)
	datastream = None
	while datastream is None:
		datastream = i.read()
	print("%s" % datastream)
	while True:
		print("Enter data:")
		dataout = input()
		s = i.write(dataout)
		print("Checking for response...")
		datastream = None
		while datastream is None:
			datastream = i.read()
		print("%s" % datastream)
		
