#!/usr/bin/env python3

from pydoc import locate
import sdl2
from sdl2 import *

from newlog import newlog
from utils import classToString, flattenString
from sdldefs import SDL_TYPES, SDL_FUNCTIONS

logger = newlog(__name__)
class SDLDecoder():
	""" Decode incoming requests to SDL function calls """

	def __init__(self, sdl_environment):
		self.environment = sdl_environment
		pass

	def id_to_funcname(self, datastream = None):
		""" Look up the properties of this datastream """
		if datastream['header'] in SDL_FUNCTIONS.keys():
		
			sdl_func = SDL_FUNCTIONS[datastream['header']]
			# Record the ID of the function
			sdl_func['ID'] = datastream['header']
	
			# Function ID is a genuine SDL function name
			if len(datastream['data']) ==  len(sdl_func['PARAMS_LIST']):
				# Correct number of parameters supplied
				return sdl_func
			else:
				# Incorrect number of parameters supplied
				logger.error("Error - incorrect number of SDL parameters supplied")
				logger.error("Error - supplied %s, requires %s" % (len(datastream['data']), len(sdl_func['PARAMS_LIST'])))
				return False
		else:
			logger.error("Error - not a valid SDL function ID: %s" %(datastream['header']))
			return False

	def construct_call(self, sdl_func = None, datastream = None):
		""" Constructs an SDL function call based on the received datastream """
		
		pos = 0
		parsed_args = []
		logger.debug(datastream)
		try:
			for arg in datastream['data']:
				if pos < len(sdl_func['PARAMS_LIST']):
					arg_types_ = sdl_func['PARAMS_LIST'][pos]
					arg_types = []
					if type(arg_types_) != type([]):
						arg_types.append(arg_types_)
					else:
						arg_types = arg_types_
					logger.debug("Checking %s for match against %s" % (arg, arg_types))
					for arg_type in arg_types:
						if arg_type in SDL_TYPES:
							# Lookup and return actual SDL object
							try:
								arg_value = self.environment.objects[arg_type][str(arg)]
								logger.debug("Adding SDL object id for %s" % arg_value)
								parsed_args.append(arg_value)
							except Exception as e:
								logger.warn("Warning unable to find self.environment.objects.%s.%s" % (arg_type, arg))
								logger.warn("Error was %s" % (e))
								#return (False, None)
						else:
							# Cast the argument value to the type as defined
							try:
								if type(arg) == type(arg_type):
									logger.debug("Adding value %s" % arg)
									parsed_args.append(arg)
								else:
									logger.debug("Adding cast value %s" % arg)
									arg_value = arg_type(arg)
									parsed_args.append(arg_value)
							except Exception as e:
								logger.warn("Warning unable to cast argument %s to %s" % (arg, arg_type))
								logger.warn("Error was %s" % (e))
								#return (False, None)
						
				else:
					logger.error("Error trying to parse argument %s, only %s arguments expected" % (pos, len(sdl_func['PARAMS_LIST'])))
				pos += 1
			real_func = sdl_func['SDL_CALL']
			
			# Anything with a trailing '_' on the function name is a wrapper
			# and we shall always supply a copy of the SDL environment
			# with that call as the first parameter...
			if sdl_func['SDL_CALL'].__name__[-1] == "_":
				parsed_args.insert(0, self.environment)
				
			if len(parsed_args) < len(datastream['data']):
				logger.error("Error constructing SDL function call")
				logger.error("Error not enough arguments parsed, %s instead of %s" % (len(parsed_args), len(datastream['data'])))
				#print("%s: ERROR %s" (__class__.__name__, parsed_args))
				print(parsed_args)
				return (False, None)
				
			if len(parsed_args) == 0:
				parsed_args = None
				
			logger.debug(parsed_args)
			return (real_func, parsed_args)
		except Exception as e:
			logger.error("Error constructing SDL function call")
			logger.error("Error sdl_func: %s" % (sdl_func))
			logger.error("Error was: %s" % (e))
				
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
		
		logger.info("Calling: %s with args %s" %  (real_func.__name__, parsed_args))
		try:
			if parsed_args is not None:
				r = real_func(*parsed_args)
			else:
				r = real_func()
			logger.info("SDL call returned %s" % (r))
			
			# If the return type was an SDL object, we have to store it in the environment
			if sdl_func['RETURN_PARAM'] in SDL_TYPES:
				object_id = self.environment.store_object(sdl_func['RETURN_PARAM'], r)
				logger.debug("Sending SDL object id %s" % (object_id))
				result['type'] = sdl_func['RETURN_PARAM']
				result['value'] = object_id
			else:
				result['type'] = classToString(sdl_func['RETURN_PARAM'])
				if sdl_func['RETURN_PARAM'] is not None:
					cast_func = sdl_func['RETURN_PARAM']
					logger.debug("Casting to %s" % (sdl_func['RETURN_PARAM']))
					logger.debug("Sending type %s" % (result['type']))
					r = cast_func(r)
					result['value'] = r
				
				logger.debug("Sending value %s" % (result['value']))
			result['status'] = 1
			return result
		except Exception as e:
			logger.error("Error while executing SDL call")
			logger.error("Error was: %s" % (e))
			result['status'] = 0
			return result
		
	def encode_result(self, sdl_func = None, result = None):
		""" Encode a result object into a string for sending back to the client """
		
		if result['status'] == 0:
			if sdl_func is None:
				datastream = "<id:;status:0;type:;value:>"			
			else:
				datastream = "<id:%s;status:0;type:;value:>" % sdl_func['ID']
		else:
			if sdl_func['RETURN_PARAM'] in SDL_TYPES:
				datastream = "<id:%s;status:%s;type:%s;value:%s>" % (sdl_func['ID'], result['status'], sdl_func['RETURN_PARAM'], result['value'])
			else:
				datastream = "<id:%s;status:%s;type:%s;value:%s>" % (sdl_func['ID'], result['status'], result['type'], result['value'])

		logger.debug("Encoded datastream %s" % (datastream))
		return datastream

class SDLEnvironment():
	""" An object which holds all of the created SDL objects """

	def __init__(self):

		logger.info("Initialising global SDL environment class")

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
			logger.debug("Adding %s data store" % (object_type))
			self.objects[object_type] = {}
		logger.info("SDL environment initialised")
		self.object_id = 0

	def store_object(self, object_type, sdl_object):
		""" Store a new SDL object """
	
		self.object_id += 1	
		logger.info("Storing new SDL object %s with ID %s" % (object_type, self.object_id))
		self.objects[object_type][str(self.object_id)] = sdl_object
		
		return self.object_id

	################################
	#
	# Any needed wrappers around original libSDL 
	# functions....
	#
	################################
	
