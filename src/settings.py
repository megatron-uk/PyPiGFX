#!/usr/bin/env python3

# Enable INFO level log messages
INFO = False
# Enable DEBUG level log messages
DEBUG = False

#IO_MODE = "pipe"
IO_MODE = "serial"
#IO_MODE = "usb"
#IO_MODE = "i2c"
#IO_MODE = "spi"

FIFO_CLIENT_NAME = "/tmp/pypigfx_client.fifo"
FIFO_MASTER_NAME = "/tmp/pypigfx_master.fifo"
USB_DEVICE = "/dev/ttyUSB0"

PTS_SERVER = "/dev/pts/0"
PTS_CLIENT = "/dev/pts/1"

# Where the generated libraries of functions are stored
LIB_LOCATION_PY = "examples/python/sdl.py"
LIB_LOCATION_C = "examples/c/sdl.c"
LIB_LOCATION_H = "examples/c/sdl.h"

# Maximum number of reads we will try to
# get a response with, before considering it 'dead'
MAX_RETRIES = 99

# Timetout for waiting for responses to a function call, in seconds
TIMEOUT = 0.25

# How long to wait for FIFO/device to become read
INITIAL_SLEEP = 3
