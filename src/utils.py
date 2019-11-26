#!/usr/bin/env python3

from newlog import newlog
logger = newlog(__name__)

def packetValid(data):
	if data[0] == '<' and data[-1] == '>':
		return True
	else:
		return False

def packetUnwrap(data):
	""" Unwrap a data sequence from an incoming client message into a Python dictionary """
	try:
		
		data = data.replace('>', '').replace('<', '')
		d_head = data.split('(')[0]
		d_body = data.split('(')[1]
		if len(d_body) > 1:
			datastream = {
				'header' : d_head,
			}
			raw_data = d_body.replace(')', '').split(',')
			new_data = []
			for d in raw_data:
				if d == '':
					logger.debug("Converting to NoneType")
					d = None
				new_data.append(d)
			datastream['data'] = new_data
		else:
			datastream = {
				'header' : d_head,
				'data' : []
			}
	except Exception as e:
		logger.error("Error corrupt data: %s" % (data))
		logger.error("Error was: %s" % (e))
		datastream = False
	return datastream

def responseUnwrap(data):
	""" Unwrap a response message from an incoming master message into a Python dictionary """
	d_split = []
	try:
		data = data.replace('>', '').replace('<', '')
		d_split = data.split(';')
		d_status_list = d_split[0].split(':')
		if len(d_status_list)>1:
			d_status = d_status_list[1]
		else:
			d_status = False
		d_type_list = d_split[1].split(':')
		if len(d_type_list)>1:
			d_type = d_type_list[1]
		else:
			d_type = False
		d_value_list = d_split[2].split(':')
		if len(d_value_list)>1:
			d_value = d_value_list[1]
			if d_value == '':
				d_value = None
		else:
			d_value = False
		datastream = {
			'status' : d_status,
			'type'	: d_type,
			'value' : d_value
		}
		return datastream
	except Exception as e:
		logger.error("Error corrupt data: %s" % (data))
		logger.error("Error was: %s" % (e))
		datastream = {
			'status' : False,
			'type' : False,
			'value' : False
		}
		return datastream

def classToString(classType = None):

	if classType is None:
		return "void"

	if classType is str:
		return "str"

	if classType is int:
		return "int"

	if classType is flattenString:
		return "str"

	logger.error("Error no class mapping for %s" % (classType))
	return classType

def flattenString(result = None):

	encoding = 'ascii'
	result = str(result.decode(encoding))
	return result
