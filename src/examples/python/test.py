#!/usr/bin/env python3

from sdl import *

v = SDL_Quit()
print(v)

v = SDL_Init(32)
print(v)

v = SDL_GetCurrentVideoDriver()
print(v)
