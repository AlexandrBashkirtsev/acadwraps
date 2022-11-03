from pathlib import Path
import os
import win32com.client
import pythoncom
import uuid
from functools import wraps
import array

import time

from pyautocad import APoint

# import settings
from . import BASE_DIR, ACAD, DOC

def ACADPoint(x,y):
	z=0 # z coordinate not used in this project
	return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x,y,z))

""" decorators"""
def propertyGetter(propertyName):
	def actual_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):

			if args[0].instance:
				for prop in args[0].props:
					if prop.PropertyName == propertyName:
						return prop.Value
		#return func(*args, **kwargs)

		return wrapper
	return actual_decorator

def propertySetter(propertyName):
	def actual_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):

			if args[0].instance:
				for prop in args[0].props:
					if prop.PropertyName == propertyName:
						prop.Value = args[1]
		#return func(*args, **kwargs)

		return wrapper
	return actual_decorator

def attributeGetter(attributeName):
	def actual_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):

			if args[0].instance:
				for attrib in args[0].attrs:
					if attrib.TagString == attributeName:
						return attrib.TextString
		#return func(*args, **kwargs)

		return wrapper
	return actual_decorator

def attributeSetter(attributeName):
	def actual_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):

			if args[0].instance:
				for attrib in args[0].attrs:
					if attrib.TagString == attributeName:
						attrib.TextString = args[1]
		#return func(*args, **kwargs)

		return wrapper
	return actual_decorator

class ACADBlock:

	"""
	ACADBlock objects store information about inserted blocks.
	On obj initialization, block inserted in active document from associated dwg file.
	Attributes of block set on initialization."""

	def __init__(self, insertionPoint, *args, **kwargs):

		self._insertionPoint 	= ACADPoint(insertionPoint[0], insertionPoint[1])
		#self.insertionPoint		= array.array('d', [insertionPoint[0],insertionPoint[1],0])
		self.attrs 				= kwargs
		self.tags 				= []

		for TagString, TextString in self.attrs.items():

			self.tags.append(TagString)

		self.blockID 			= str(uuid.uuid4())

		self.path 				= "path/to/dwg"		# path to dwg file
		self.blockName 			= "blockName" # empty by default
		self.acadEntityName		= "AcDbBlockReference"
		self.scale				= 1
		self.rotation			= 0

		self.instance 			= None # instcance of ACAD block

		self.props 				= None

	@property
	def insertionPoint(self):
		return self._insertionPoint

	@insertionPoint.setter
	def insertionPoint(self, point):
		self.insertionPoint = ACADPoint(point[0], point[1])

	"""attributes"""
	@property
	@attributeGetter("ID")
	def ID(self):
		pass

	@ID.setter
	@attributeSetter("ID")
	def ID(self):
		pass

	def getInstance(self):

		"""
		getInstance function returns instance of this block in DOC, if present"""

		for entity in DOC.PaperSpace:
			name = entity.EntityName
			if name == self.acadEntityName:
				# this is block, inserted in PaperSpace
				HasAttributes = entity.HasAttributes
				if HasAttributes:
					for attrib in entity.GetAttributes():
						if attrib.TextString == self.blockID:
							self.instance = entity
							return self.instance

		print("Block with {self.blockID} is not found")

	def get_properties(self):
		# block must be inserted in PaperSpace or ModelSpace before calling that function
		if self.instance:
			print("Block.GetDynamicBlockProperties. ID: ", self.blockID)
			for prop in self.instance.GetDynamicBlockProperties():
				print("Name: ", prop.PropertyName)
				print("Read only: ", prop.ReadOnly)
				print("Description: ", prop.Description)
				print("Value: ", prop.Value)
				print("AllowedValues: ", prop.AllowedValues)
				print("--------------------")

class A3TitleBlockPower(ACADBlock):

	"""
	A3 Paper with secondary form block definition"""

	def __init__(self, insertionPoint, **kwargs):

		super().__init__(insertionPoint, **kwargs)

		self.path 				= os.path.join(BASE_DIR, "blocks", "a3title_power_scheme.dwg")	# path to dwg file
		self.blockName 			= "title_page_next" # empty by default
		# self.scale			= 0.0393701 		# inches to mm
		self.scale				= 1 				# inches to mm

		"""
		for TagString, TextString in self.attrs.items():

			if TagString == "TITLE_TEXT":
				self.attrs["TITLE_TEXT_MIRRORED"] = self.attrs["TITLE_TEXT"]
				self.tags.append("TITLE_TEXT_MIRRORED")
				break
		"""

	"""attributes"""
	@property
	@attributeGetter("TITLE_TEXT_MIRRORED")
	def TITLE_TEXT_MIRRORED(self):
		pass

	@TITLE_TEXT_MIRRORED.setter
	@attributeSetter("TITLE_TEXT_MIRRORED")
	def TITLE_TEXT_MIRRORED(self):
		pass

	@property
	@attributeGetter("TITLE_TEXT")
	def TITLE_TEXT(self):
		pass

	@TITLE_TEXT.setter
	@attributeSetter("TITLE_TEXT")
	def TITLE_TEXT(self):
		self.TITLE_TEXT_MIRRORED = self.TITLE_TEXT

	@property
	@attributeGetter("NUM")
	def NUM(self):
		pass

	@NUM.setter
	@attributeSetter("NUM")
	def NUM(self):
		pass

	@property
	@attributeGetter("DESCR_SHORT")
	def DESCR_SHORT(self):
		pass

	@DESCR_SHORT.setter
	@attributeSetter("DESCR_SHORT")
	def DESCR_SHORT(self):
		pass

	@property
	@attributeGetter("POWER_SOURCE_1")
	def POWER_SOURCE_1(self):
		pass

	@POWER_SOURCE_1.setter
	@attributeSetter("POWER_SOURCE_1")
	def POWER_SOURCE_1(self):
		pass

	@property
	@attributeGetter("POWER_SOURCE_2")
	def POWER_SOURCE_2(self):
		pass

	@POWER_SOURCE_2.setter
	@attributeSetter("POWER_SOURCE_2")
	def POWER_SOURCE_2(self):
		pass

	@property
	@attributeGetter("POWER_RESERVE")
	def POWER_RESERVE(self):
		pass

	@POWER_RESERVE.setter
	@attributeSetter("POWER_RESERVE")
	def POWER_RESERVE(self):
		pass


class A3SecondaryBlock(ACADBlock):

	"""
	A3 Paper with secondary form block definition"""

	def __init__(self, insertionPoint, **kwargs):

		super().__init__(insertionPoint, **kwargs)

		self.path 				= os.path.join(BASE_DIR, "blocks", "a3secondary.dwg")	# path to dwg file
		self.blockName 			= "title_page_next" # empty by default
		# self.scale			= 0.0393701 		# inches to mm
		self.scale				= 1 				# inches to mm

		"""
		for TagString, TextString in self.attrs.items():

			if TagString == "TITLE_TEXT":
				self.attrs["TITLE_TEXT_MIRRORED"] = self.attrs["TITLE_TEXT"]
				self.tags.append("TITLE_TEXT_MIRRORED")
				break
		"""

	"""attributes"""
	@property
	@attributeGetter("TITLE_TEXT_MIRRORED")
	def TITLE_TEXT_MIRRORED(self):
		pass

	@TITLE_TEXT_MIRRORED.setter
	@attributeSetter("TITLE_TEXT_MIRRORED")
	def TITLE_TEXT_MIRRORED(self):
		pass

	@property
	@attributeGetter("TITLE_TEXT")
	def TITLE_TEXT(self):
		pass

	@TITLE_TEXT.setter
	@attributeSetter("TITLE_TEXT")
	def TITLE_TEXT(self):
		self.TITLE_TEXT_MIRRORED = self.TITLE_TEXT

	@property
	@attributeGetter("NUMBER")
	def NUMBER(self):
		pass

	@NUMBER.setter
	@attributeSetter("NUMBER")
	def NUMBER(self):
		pass

class PLCInputBlock(ACADBlock):

	"""
	PLC input block definition"""

	def __init__(self, insertionPoint, **kwargs):

		super().__init__(insertionPoint, **kwargs)

		self.path 				= os.path.join(BASE_DIR, "blocks", "plc_input_contact.dwg")	# path to dwg file
		self.blockName 			= "plc_input_block" # empty by default
		# self.scale				= 0.0393701 		# inches to mm
		self.scale				= 1
		self.height 			= 10.0

	"""properties"""
	@property
	@propertyGetter("VISIBILITY")
	def VISIBILITY(self):
		pass

	@VISIBILITY.setter
	@propertySetter("VISIBILITY")
	def VISIBILITY(self):
		pass

	@property
	@propertyGetter("SHIFT")
	def SHIFT(self):
		pass

	@SHIFT.setter
	@propertySetter("SHIFT")
	def SHIFT(self):
		pass

	"""attributes"""
	@property
	@attributeGetter("NAME")
	def NAME(self):
		pass

	@NAME.setter
	@attributeSetter("NAME")
	def NAME(self):
		pass
	
	@property
	@attributeGetter("NUM")
	def NUM(self):
		pass

	@NUM.setter
	@attributeSetter("NUM")
	def NUM(self):
		pass

	@property
	@attributeGetter("CONTACT")
	def CONTACT(self):
		pass

	@CONTACT.setter
	@attributeSetter("CONTACT")
	def CONTACT(self):
		pass
	
	@property
	@attributeGetter("CLEMM_1")
	def CLEMM_1(self):
		pass

	@CLEMM_1.setter
	@attributeSetter("CLEMM_1")
	def CLEMM_1(self):
		pass

	@property
	@attributeGetter("CLEMM_2")
	def CLEMM_2(self):
		pass

	@CLEMM_2.setter
	@attributeSetter("CLEMM_2")
	def CLEMM_2(self):
		pass

	@property
	@attributeGetter("MARKER_1")
	def MARKER_1(self):
		pass

	@MARKER_1.setter
	@attributeSetter("MARKER_1")
	def MARKER_1(self):
		pass

	@property
	@attributeGetter("MARKER_2")
	def MARKER_2(self):
		pass

	@MARKER_2.setter
	@attributeSetter("MARKER_2")
	def MARKER_2(self):
		pass

	@property
	@attributeGetter("R_CLEMM_1")
	def R_CLEMM_1(self):
		pass

	@R_CLEMM_1.setter
	@attributeSetter("R_CLEMM_1")
	def R_CLEMM_1(self):
		pass

	@property
	@attributeGetter("R_CLEMM_2")
	def R_CLEMM_2(self):
		pass

	@R_CLEMM_2.setter
	@attributeSetter("R_CLEMM_2")
	def R_CLEMM_2(self):
		pass

	@property
	@attributeGetter("R_MARKER_1")
	def R_MARKER_1(self):
		pass

	@R_MARKER_1.setter
	@attributeSetter("R_MARKER_1")
	def R_MARKER_1(self):
		pass

	@property
	@attributeGetter("R_MARKER_2")
	def R_MARKER_2(self):
		pass

	@R_MARKER_2.setter
	@attributeSetter("R_MARKER_2")
	def R_MARKER_2(self):
		pass

	@property
	@attributeGetter("POWER")
	def POWER(self):
		pass

	@POWER.setter
	@attributeSetter("POWER")
	def POWER(self):
		pass

	@property
	@attributeGetter("POWER_SIMPLE")
	def POWER_SIMPLE(self):
		pass

	@POWER_SIMPLE.setter
	@attributeSetter("POWER_SIMPLE")
	def POWER_SIMPLE(self):
		pass

class PLCAnalogInputBlock(ACADBlock):

	"""
	PLC input block definition"""

	def __init__(self, insertionPoint, **kwargs):

		super().__init__(insertionPoint, **kwargs)

		self.path 				= os.path.join(BASE_DIR, "blocks", "plc_analog_input.dwg")	# path to dwg file
		self.blockName 			= "plc_input_block" # empty by default
		# self.scale				= 0.0393701 		# inches to mm
		self.scale				= 1
		self.height 			= 10.0

	"""properties"""
	@property
	@propertyGetter("VISIBILITY")
	def VISIBILITY(self):
		pass

	@VISIBILITY.setter
	@propertySetter("VISIBILITY")
	def VISIBILITY(self):
		pass

	"""attributes"""
	@property
	@attributeGetter("NAME")
	def NAME(self):
		pass

	@NAME.setter
	@attributeSetter("NAME")
	def NAME(self):
		pass

	@property
	@attributeGetter("V")
	def V(self):
		pass

	@V.setter
	@attributeSetter("V")
	def V(self):
		pass

	@property
	@attributeGetter("I")
	def I(self):
		pass

	@I.setter
	@attributeSetter("I")
	def I(self):
		pass

	@property
	@attributeGetter("VI")
	def VI(self):
		pass

	@VI.setter
	@attributeSetter("VI")
	def VI(self):
		pass

	@property
	@attributeGetter("CLEMM_1")
	def CLEMM_1(self):
		pass

	@CLEMM_1.setter
	@attributeSetter("CLEMM_1")
	def CLEMM_1(self):
		pass

	@property
	@attributeGetter("CLEMM_2")
	def CLEMM_2(self):
		pass

	@CLEMM_2.setter
	@attributeSetter("CLEMM_2")
	def CLEMM_2(self):
		pass

	@property
	@attributeGetter("CLEMM_3")
	def CLEMM_3(self):
		pass

	@CLEMM_3.setter
	@attributeSetter("CLEMM_3")
	def CLEMM_3(self):
		pass

	@property
	@attributeGetter("POWER_1")
	def POWER_1(self):
		pass

	@POWER_1.setter
	@attributeSetter("POWER_1")
	def POWER_1(self):
		pass

	@property
	@attributeGetter("POWER_2")
	def POWER_2(self):
		pass

	@POWER_2.setter
	@attributeSetter("POWER_2")
	def POWER_2(self):
		pass

	@property
	@attributeGetter("MARKER_1")
	def MARKER_1(self):
		pass

	@MARKER_1.setter
	@attributeSetter("MARKER_1")
	def MARKER_1(self):
		pass

	@property
	@attributeGetter("MARKER_2")
	def MARKER_2(self):
		pass

	@MARKER_2.setter
	@attributeSetter("MARKER_2")
	def MARKER_2(self):
		pass

	@property
	@attributeGetter("MARKER_3")
	def MARKER_3(self):
		pass

	@MARKER_3.setter
	@attributeSetter("MARKER_3")
	def MARKER_3(self):
		pass

	@property
	@attributeGetter("MARKER_4")
	def MARKER_4(self):
		pass

	@MARKER_4.setter
	@attributeSetter("MARKER_4")
	def MARKER_4(self):
		pass

	@property
	@attributeGetter("MARKER_5")
	def MARKER_5(self):
		pass

	@MARKER_5.setter
	@attributeSetter("MARKER_5")
	def MARKER_5(self):
		pass