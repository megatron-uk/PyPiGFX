#!/usr/bin/env python3

from sdl2 import *
from utils import flattenString

SDL_TYPES = ["SDL_Rect", "SDL_Surface", "SDL_Window", "SDL_Renderer"]

SDL_FUNCTIONS = {
        "00" : {
                "SDL_NAME" : "SDL_Quit",
                "SDL_CALL" : SDL_Quit,
                "PARAMS_LIST" : [],
                "RETURN_PARAM" : None
        },
        "01" : {
                "SDL_NAME" : "SDL_Init",
                "SDL_CALL" : SDL_Init,
                "PARAMS_LIST" : [int],
                "RETURN_PARAM" : int
        },
        "02" : {
        	"SDL_NAME" : "SDL_GetCurrentVideoDriver",
        	"SDL_CALL" : SDL_GetCurrentVideoDriver,
        	"PARAMS_LIST" : [],
        	"RETURN_PARAM" : flattenString
        },
        "03" : {
        	"SDL_NAME" : "SDL_CreateWindow",
        	"SDL_CALL" : SDL_CreateWindow,
        	"PARAMS_LIST" : [str.encode, int, int, int, int, int],
        	"RETURN_PARAM" : "SDL_Window"
        },
        "04" : {
        	"SDL_NAME" : "SDL_CreateRenderer",
        	"SDL_CALL" : SDL_CreateRenderer,
        	"PARAMS_LIST" : ["SDL_Window", int, int, int],
        	"RETURN_PARAM" : "SDL_Renderer"
        },
	"05" : {
		"SDL_NAME" : "SDL_CreateRGBSurface",
		"SDL_CALL" : SDL_CreateRGBSurface,
		"PARAMS_LIST" : [int, int, int, int, int, int, int, int],
		"RETURN_PARAM" : "SDL_Surface"
	},
	"06" : {
		"SDL_NAME" : "SDL_MapRGB",
		"SDL_CALL" : SDL_MapRGB_,
		"PARAMS_LIST" : ["SDL_PixelFormat", int, int, int],
		"RETURN_PARAM" : int
	},
        "9999" : {
                "SDL_NAME" : "SDL_BlitSurface",
                "SDL_CALL" : SDL_BlitSurface,
                "PARAMS_LIST" : ["SDL_Surface", "SDL_Rect", "SDL_Surface", "SDL_Rect"],
                "RETURN_PARAM" : int
        }
}
