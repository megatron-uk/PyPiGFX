#!/usr/bin/env python3

from sdl2 import *

SDL_TYPES = ["SDL_Rect", "SDL_Surface", "SDL_Window", "SDL_Renderer"]

SDL_FUNCTIONS = {
        "0000" : {
                "SDL_NAME" : "SDL_Quit",
                "SDL_CALL" : SDL_Quit,
                "PARAMS_LIST" : [],
                "RETURN_PARAM" : None
        },
        "0001" : {
                "SDL_NAME" : "SDL_Init",
                "SDL_CALL" : SDL_Init,
                "PARAMS_LIST" : [int],
                "RETURN_PARAM" : int
        },
        "0002" : {
        	"SDL_NAME" : "SDL_GetCurrentVideoDriver",
        	"SDL_CALL" : SDL_GetCurrentVideoDriver,
        	"PARAMS_LIST" : [],
        	"RETURN_PARAM" : str
        },
        "0003" : {
        	"SDL_NAME" : "SDL_CreateWindow",
        	"SDL_CALL" : SDL_CreateWindow,
        	"PARAMS_LIST" : [str.encode, int, int, int, int, int],
        	"RETURN_PARAM" : "SDL_Window"
        },
        "0004" : {
        	"SDL_NAME" : "SDL_CreateRenderer",
        	"SDL_CALL" : SDL_CreateRenderer,
        	"PARAMS_LIST" : ["SDL_Window", int, int, int],
        	"RETURN_PARAM" : "SDL_Renderer"
        },
        
        "9999" : {
                "SDL_NAME" : "SDL_BlitSurface",
                "SDL_CALL" : SDL_BlitSurface,
                "PARAMS_LIST" : ["SDL_Surface", "SDL_Rect", "SDL_Surface", "SDL_Rect"],
                "RETURN_PARAM" : int
        }
}
