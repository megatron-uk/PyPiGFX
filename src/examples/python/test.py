#!/usr/bin/env python3

import sys
import datetime
import time
from sdl import *

print("Closing any existing SDL session")
v = SDL_Quit()
time.sleep(3)

v = SDL_Init(32)
if v:
	print("SDL initialised")
else:
	print("Unable to initialise SDL")
	sys.exit(1)

v = SDL_GetCurrentVideoDriver()
if v:
	print("Current video driver is %s" % v)
else:
	print("Unable to query video driver")
	sys.exit(1)

window = SDL_CreateWindow("test",0,0,640,480,0)
if window:
	print("Created window with ID %s" % window)
else:
	print("Unable to create window")
	sys.exit(1)


renderer = SDL_CreateRenderer(window,0,0)
if renderer:
	print("Created renderer with ID %s" % renderer)	
else:
	print("Unable to create renderer")
	sys.exit(1)

surface = SDL_CreateRGBSurface(0,640,480,24,0,0,0,255)
if surface:
	print("Created surface with ID %s" % surface)
else:
	print("Unable to create surface")
	sys.exit(1)

black = SDL_MapRGB(surface,0,0,0)
print(black)
white = SDL_MapRGB(surface,255,255,255)
print(white)
green = SDL_MapRGB(surface,0,255,0)
print(green)
red = SDL_MapRGB(surface,255,0,0)
print(red)


# Create a white rectangle that moves back and forth
#box = SDL_Rect
col = black

t1 = datetime.datetime.now()
# Fill the surface in black
v = SDL_FillRect(surface,None,col)
t2 = datetime.datetime.now()

# Transfer surface to a texture...
texture = SDL_CreateTextureFromSurface(renderer, surface)
t3 = datetime.datetime.now()

# ...and present to the renderer
v = SDL_RenderCopy(renderer,texture,None,None)	
t4 = datetime.datetime.now()

# ...finally, update screen
v = SDL_RenderPresent(renderer)
t5 = datetime.datetime.now()

print("=====================")
print("SDL_Fillrect: 			%.1f ms" % (((t2 - t1).total_seconds()) * 1000))
print("SDL_CreateTextureFromSurface:	%.1f ms" % (((t3 - t2).total_seconds()) * 1000))
print("SDL_RenderCopy:			%.1f ms" % (((t4 - t3).total_seconds()) * 1000))
print("SDL_RenderPresent:		%.1f ms" % (((t5 - t4).total_seconds()) * 1000))
print("=====================")
print("Total: 				%.1f ms" % (((t5 - t1).total_seconds()) * 1000))
print("Effective FPS:			%.1f fps" % (1000 / (((t5 - t1).total_seconds()) * 1000)))
print("=====================")

print("")
print("Begin screen cycle test at 5Hz:")

for i in range(0,20):
	for col in [black,white]:
		t1 = datetime.datetime.now()
		v = SDL_FillRect(surface,None,col)
		texture = SDL_CreateTextureFromSurface(renderer, surface)
		v = SDL_RenderCopy(renderer,texture,None,None)
		v = SDL_RenderPresent(renderer)
		t2 = datetime.datetime.now()
		t = (((t2 - t1).total_seconds()) * 1000)
		if t > 200:
			print("Late frame: %.2f ms" % t)
		else:
			s = 0.2 - (t / 1000)
			#print("Sleeping: %.2f ms" % (s * 1000))
			time.sleep(s)
	
print("")
print("Begin screen cycle test at 10Hz:")

for i in range(0,30):
	for col in [green,black]:
		t1 = datetime.datetime.now()
		v = SDL_FillRect(surface,None,col)
		texture = SDL_CreateTextureFromSurface(renderer, surface)
		v = SDL_RenderCopy(renderer,texture,None,None)
		v = SDL_RenderPresent(renderer)
		t2 = datetime.datetime.now()
		t = (((t2 - t1).total_seconds()) * 1000)
		if t > 100:
			print("Late frame: %.2f ms" % t)
		else:
			s = 0.1 - (t / 1000)
			#print("Sleeping: %.2f ms" % (s * 1000))
			if s > 0:
				time.sleep(s)
	
print("")
print("Begin screen cycle test at 20Hz:")

for i in range(0,50):
	for col in [red,black]:
		t1 = datetime.datetime.now()
		v = SDL_FillRect(surface,None,col)
		texture = SDL_CreateTextureFromSurface(renderer, surface)
		v = SDL_RenderCopy(renderer,texture,None,None)
		v = SDL_RenderPresent(renderer)
		t2 = datetime.datetime.now()
		t = (((t2 - t1).total_seconds()) * 1000)
		if t > 50:
			print("Late frame: %.2f ms" % t)
		else:
			s = 0.05 - (t / 1000)
			#print("Sleeping: %.2f ms" % (s * 1000))
			if s > 0:
				time.sleep(s)
				
print("")
print("Begin screen cycle test at 50Hz:")

for i in range(0,70):
	for col in [red,green]:
		t1 = datetime.datetime.now()
		v = SDL_FillRect(surface,None,col)
		texture = SDL_CreateTextureFromSurface(renderer, surface)
		v = SDL_RenderCopy(renderer,texture,None,None)
		v = SDL_RenderPresent(renderer)
		t2 = datetime.datetime.now()
		t = (((t2 - t1).total_seconds()) * 1000)
		if t > 20:
			print("Late frame: %.2f ms" % t)
		else:
			s = 0.02 - (t / 1000)
			#print("Sleeping: %.2f ms" % (s * 1000))
			if s > 0:
				time.sleep(s)