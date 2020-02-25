#!/usr/bin/env python3

from sdl2 import *

def SDL_MapRGB_(SDL_environment, SDL_surface, r, g, b):
	""" Wrapper around native SDL_MapRGB to instead lookup SDL_PixelMap
	data from the current surface. """
	
	return SDL_MapRGB(SDL_surface.contents.format, r, g, b)

def SDL_Quit_(SDL_environment):
	""" Wrapper around native SDL_Quit to also clean up any cached objects
	from the SDL_environment. """

	for object_type in SDL_environment.objects.keys():
		SDL_environment.objects[object_type] = {}
	return SDL_Quit()
