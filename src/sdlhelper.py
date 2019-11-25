#!/usr/bin/env python3

from pydoc import locate
import sdl2
from sdl2 import *

from utils import classToString, flattenString
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
				print("%s : ERROR: Supplied %s, Requires %s" % (__class__.__name__, len(datastream['data']), len(sdl_func['PARAMS_LIST'])))
				return False
		else:
			print("%s : ERROR: Not a valid SDL function ID" % (__class__.__name__))
			return False

	def construct_call(self, sdl_func = None, datastream = None):
			""" Constructs an SDL function call based on the received datastream """
		
			pos = 0
			parsed_args = []
			print(datastream)
		#try:
			for arg in datastream['data']:
				if pos < len(sdl_func['PARAMS_LIST']):
					arg_types_ = sdl_func['PARAMS_LIST'][pos]
					arg_types = []
					if type(arg_types_) != type([]):
						arg_types.append(arg_types_)
					else:
						arg_types = arg_types_
					print("checking %s for match against %s" % (arg, arg_types))
					for arg_type in arg_types:
						if arg_type in SDL_TYPES:
							# Lookup and return actual SDL object
							try:
								arg_value = self.environment.objects[arg_type][str(arg)]
								print("adding SDL object id for %s" % arg_value)
								parsed_args.append(arg_value)
							except Exception as e:
								print("%s: Warning unable to find self.environment.objects.%s.%s" % (__class__.__name__, arg_type, arg))
								print("%s: %s" % (__class__.__name__, e))
								#return (False, None)
						else:
							# Cast the argument value to the type as defined
							try:
								if type(arg) == type(arg_type):
									print("adding value %s" % arg)
									parsed_args.append(arg)
								else:
									print("adding cast value %s" % arg)
									arg_value = arg_type(arg)
									parsed_args.append(arg_value)
							except Exception as e:
								print("%s: Warning unable to cast argument %s to %s" % (__class__.__name__, arg, arg_type))
								print("%s: %s" % (__class__.__name__, e))
								#return (False, None)
						
				else:
					print("%s: Error trying to parse argument %s, only %s arguments expected" % (__class__.__name__, pos, len(sdl_func['PARAMS_LIST'])))
				pos += 1
			real_func = sdl_func['SDL_CALL']
			
			# Anything with a trailing '_' on the function name is a wrapper
			# and we shall always supply a copy of the SDL environment
			# with that call as the first parameter...
			if sdl_func['SDL_CALL'].__name__[-1] == "_":
				parsed_args.insert(0, self.environment)
				
			if len(parsed_args) < len(datastream['data']):
				print("%s: ERROR constructing SDL function call" % (__class__.__name__))
				print("%s: ERROR not enough arguments parsed, %s instead of %s" % (__class__.__name__, len(parsed_args), len(datastream['data'])))
				#print("%s: ERROR %s" (__class__.__name__, parsed_args))
				print(parsed_args)
				return (False, None)
				
			if len(parsed_args) == 0:
				parsed_args = None
				
			print(parsed_args)
			return (real_func, parsed_args)
		#except Exception as e:
			print("%s: ERROR constructing SDL function call" % (__class__.__name__))
			print("%s: ERROR: sdl_func: %s" % (__class__.__name__, sdl_func))
			print("%s: ERROR: %s" % (__class__.__name__, e))
				
			return (False, None)
		
	def result(self):
		data = {
			'status' : 0,
			'type'	: 'void',
			'value'	: ''
		}
		return data
		
	def execute_call(self, sdl_func = None, real_func = None, parsed_args = None):
			""" Call the constructed SDL function """
		
			result = self.result()
		
			print("%s: Calling: %s with args %s" %  (__class__.__name__, real_func.__name__, parsed_args))
		#try:
			if parsed_args is not None:
				r = real_func(*parsed_args)
			else:
				r = real_func()
			print("%s: SDL call returned %s" % (__class__.__name__, r))
			
			# If the return type was an SDL object, we have to store it in the environment
			if sdl_func['RETURN_PARAM'] in SDL_TYPES:
				object_id = self.environment.store_object(sdl_func['RETURN_PARAM'], r)
				print("%s: Sending SDL object id %s" % (__class__.__name__, object_id))
				result['type'] = sdl_func['RETURN_PARAM']
				result['value'] = object_id
			else:
				result['type'] = classToString(sdl_func['RETURN_PARAM'])
				if sdl_func['RETURN_PARAM'] is not None:
					cast_func = sdl_func['RETURN_PARAM']
					print("%s: Casting to %s" % (__class__.__name__, sdl_func['RETURN_PARAM']))
					print("%s: Sending type %s" % (__class__.__name__, result['type']))
					print(r)
					r = cast_func(r)
					result['value'] = r
					print(result['value'])
				
				print("%s: Sending value %s" % (__class__.__name__, result['value']))
			result['status'] = 1
			return result
		#except Exception as e:
			print("%s: Error while executing SDL call" % (__class__.__name__))
			print("%s: %s" % (__class__.__name__, e))
			result['status'] = 0
			return result
		
	def encode_result(self, sdl_func = None, result = None):
		""" Encode a result object into a string for sending back to the client """
		
		if result['status'] == 0:
			datastream = "<status:0,type:,value:>"			
		else:
			if sdl_func['RETURN_PARAM'] in SDL_TYPES:
				datastream = "<status:%s,type:%s,value:%s>" % (result['status'], sdl_func['RETURN_PARAM'], result['value'])
			else:
				datastream = "<status:%s,type:%s,value:%s>" % (result['status'], result['type'], result['value'])

		print("%s: Encoded datastream %s" % (__class__.__name__, datastream))
		return datastream

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

		self.object_id = 0

	def store_object(self, object_type, sdl_object):
		""" Store a new SDL object """
	
		self.object_id += 1	
		self.objects[object_type][str(self.object_id)] = sdl_object
		
		return self.object_id

	################################
	#
	# Any needed wrappers around original libSDL 
	# functions....
	#
	################################
	