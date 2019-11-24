#!/usr/bin/env python3

from pydoc import locate
import sdl2
from sdl2 import *

from sdldefs import SDL_TYPES, SDL_FUNCTIONS

class SDLDecoder():
	""" Decode incoming requests to SDL function calls """

	def __init__(self, sdl_environment):
		self.environment = sdl_environment
		pass

	def id_to_funcname(self, datastream = None):
		""" Look up the properties of this datastream """
		if datastream['header'] in SDL_FUNCTIONS.keys():
		
			sdl_func = SDL_FUNCTIONS[datastream['header']]
	
			# Function ID is a genuine SDL function name
			if len(datastream['data']) ==  len(sdl_func['PARAMS_LIST']):
				# Correct number of parameters supplied
				return sdl_func
			else:
				# Incorrect number of parameters supplied
				print("%s : ERROR: Incorrect number of SDL parameters supplied" % (__class__.__name__))
				print("%s : ERROR: Supplied %s, Requires %s" % (__class__.__name__, len(datastream['data']), sdl_func['NUM_PARAMS']))
				return False
		else:
			print("%s : ERROR: Not a valid SDL function ID" % (__class__.__name__))
			return False

	def construct_call(self, sdl_func = None, datastream = None):
		""" Constructs an SDL function call based on the received datastream """
		
		pos = 0
		parsed_args = []
		for arg in datastream['data']:
			arg_type = sdl_func['PARAMS_LIST'][pos]
			
			if arg_type in SDL_TYPES:
				# Lookup and return actual SDL object
				try:
					arg_value = self.environment.objects[arg_type][arg]['object']
				except Exception as e:
					print("%s: Error unable to find self.environment.objects.%s.%s" % (arg_type, arg))
					return False
			else:
				# Cast the argument value to the type as defined
				arg_value = arg_type(arg)
			parsed_args.append(arg_value)
			
			pos += 1
		real_func = sdl_func['SDL_CALL']
		print("%s: Calling: %s with args %s" %  (__class__.__name__, real_func.__name__, parsed_args))
		r = real_func(*parsed_args)
		print("%s: SDL call returned %s" % (__class__.__name__, r))
		return r

class SDLEnvironment():
	""" An object which holds all of the created SDL objects """

	def __init__(self):

		print("%s : Initialising global SDL environment class" % (__class__.__name__))

		# Surfaces or fonts that we create
		self.surfaces = {}
		self.fonts = {}
	
		# Default to no open screens
		self.window = None
		self.backbuffer = None
		self.old_backbuffer = None
		self.render_texture = None

		# An index of all objects
		self.objects = {}
		for object_type in SDL_TYPES:
			print("%s : - Adding %s data store" % (__class__.__name__, object_type))
			self.objects[object_type] = {}

		print("%s : Done" % (__class__.__name__))
