#!/usr/bin/env python3


def packetValid(data):
	if data[0] == '<' and data[-1] == '>':
		return True
	else:
		return False

def packetUnwrap(data):
	""" Unwrap a data sequence from an incoming message into a Python dictionary """
	data = data.replace('>', '').replace('<', '')
	try:
		d_head = data.split('(')[0]
		d_body = data.split('(')[1]
		if len(d_body) > 1:
			datastream = {
				'header' : d_head,
				'data' : d_body.replace(')', '').split(',')
			}
		else:
			datastream = {
				'header' : d_head,
				'data' : []
			}
	except Exception as e:
		print("%s: Error - corrupt data: %s" % (__name__, data))
		print("%s: %s" % (__name__, e))
		datastream = False
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

	print("%s: Error no class mapping for %s" % (__name__, classType))
	return classType

def flattenString(result = None):

	encoding = 'ascii'
	result = str(result.decode(encoding))
	return result
