#!/usr/bin/env python3

from sdl2 import *

def SDL_MapRGB_(SDL_environment, SDL_surface, r, g, b):
	""" Wrapper around native SDL_MapRGB to instead lookup SDL_PixelMap
	data from the current surface. """
	
	rgb = SDL_MapRGB(SDL_surface.contents.format, r, g, b)
	return rgb