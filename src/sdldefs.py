#!/usr/bin/env python3

from sdl2 import *
from sdlwrappers import *
from utils import flattenString

SDL_TYPES = ["SDL_Rect", "SDL_Surface", "SDL_Window", "SDL_Renderer", "SDL_Texture"]

SDL_FUNCTIONS = {
        "00" : {
                "SDL_NAME" : "SDL_Quit",
                "SDL_CALL" : SDL_Quit,
		"PARAMS_NAMES" : [],
                "PARAMS_LIST" : [],
                "RETURN_PARAM" : None
        },
        "01" : {
                "SDL_NAME" : "SDL_Init",
                "SDL_CALL" : SDL_Init,
		"PARAMS_NAMES" : ["flags"],
                "PARAMS_LIST" : [int],
                "RETURN_PARAM" : int
        },
        "02" : {
        	"SDL_NAME" : "SDL_GetCurrentVideoDriver",
        	"SDL_CALL" : SDL_GetCurrentVideoDriver,
		"PARAMS_NAMES" : [],
        	"PARAMS_LIST" : [],
        	"RETURN_PARAM" : flattenString
        },
        "03" : {
        	"SDL_NAME" : "SDL_CreateWindow",
        	"SDL_CALL" : SDL_CreateWindow,
		"PARAMS_NAMES" : ["title", "x", "y", "w", "h", "bpp"],
        	"PARAMS_LIST" : [str.encode, int, int, int, int, int],
        	"RETURN_PARAM" : "SDL_Window"
        },
        "04" : {
        	"SDL_NAME" : "SDL_CreateRenderer",
        	"SDL_CALL" : SDL_CreateRenderer,
		"PARAMS_NAMES" : ["window", "index", "flags"],
        	"PARAMS_LIST" : ["SDL_Window", int, int, int],
        	"RETURN_PARAM" : "SDL_Renderer"
        },
	"05" : {
		"SDL_NAME" : "SDL_CreateRGBSurface",
		"SDL_CALL" : SDL_CreateRGBSurface,
		"PARAMS_NAMES" : ["flags", "w", "h", "bpp", "rmask", "gmask", "bmask", "alpha"],
		"PARAMS_LIST" : [int, int, int, int, int, int, int, int],
		"RETURN_PARAM" : "SDL_Surface"
	},
	"06" : {
		"SDL_NAME" : "SDL_MapRGB",
		"SDL_CALL" : SDL_MapRGB_,
		"PARAMS_NAMES" : ["surface", "r", "g", "b"],
		"PARAMS_LIST" : ["SDL_Surface", int, int, int],
		"RETURN_PARAM" : int
	},
	"07" : {
		"SDL_NAME" : "SDL_FillRect",
		"SDL_CALL" : SDL_FillRect,
		"PARAMS_NAMES" : ["surface", "rect", "rgb"],
		"PARAMS_LIST" : ["SDL_Surface", ["SDL_Rect", None], int],
		"RETURN_PARAM" : int
	},
	"08" : {
		"SDL_NAME" : "SDL_CreateTextureFromSurface",
		"SDL_CALL" : SDL_CreateTextureFromSurface,
		"PARAMS_NAMES" : ["renderer", "surface"],
		"PARAMS_LIST" : ["SDL_Renderer", "SDL_Surface"],
		"RETURN_PARAM" : "SDL_Texture"
	},
	"09" : {
		"SDL_NAME" : "SDL_RenderCopy",
		"SDL_CALL" : SDL_RenderCopy,
		"PARAMS_NAMES" : ["renderer", "surface", "rect", "rect"],
		"PARAMS_LIST" : ["SDL_Renderer", "SDL_Texture", ["SDL_Rect", None], ["SDL_Rect", None]],
		"RETURN_PARAM" : int
	},
	"0A" : {
		"SDL_NAME" : "SDL_RenderPresent",
		"SDL_CALL" : SDL_RenderPresent,
		"PARAMS_NAMES" : ["renderer"],
		"PARAMS_LIST" : ["SDL_Renderer"],
		"RETURN_PARAM" : None
	}
}
