#!/usr/bin/env python3

import sys
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

col = black
# Fill the surface in black
v = SDL_FillRect(surface,None,col)
print("SDL_FillRect %s" % v)

# Transfer surface to a texture and present to the renderer
texture = SDL_CreateTextureFromSurface(renderer, surface)
print("SDL_CreateTextureFromSurface %s" % texture)
v = SDL_RenderCopy(renderer,texture,None,None)	
print("SDL_RenderCopy %s" % v)

# Finally, update screen
v = SDL_RenderPresent(renderer)
print("SDL_RenderPresent %s" % v)

# Create a white rectangle that moves back and forth
#box = SDL_Rect
#while True:


