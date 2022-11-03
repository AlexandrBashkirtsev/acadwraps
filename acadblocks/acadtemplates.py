from pathlib import Path
import os
import win32com.client
# import pythoncom
import uuid

import time

# from pyautocad import APoint

# import settings
from . import BASE_DIR, ACAD, DOC

class AcadTemplate:
	"""
	ACAD Wrapper for abstract paper form layout"""

	def __init__(self, plotConfigName, mediaName, standardScale, name, **kwargs):

		self.kwargs = kwargs

		# make new layout and activate it
		#names = [l.name for l in DOC.Layouts]
		#layoutName = "Лист" + str(int(names[-1][-1])+1)
		self.layout = DOC.Layouts.Add(name)
		time.sleep(0.1)

		
		# check if we can print in PDF
		# if we can, then choose this configuration
		# else, object will not created
		plotDevices = self.layout.GetPlotDeviceNames()
		time.sleep(0.1)
		if plotConfigName in plotDevices:
			self.layout.ConfigName = plotConfigName
		else:
			print("No supported plotter found")
			return

		# at this point we have supported print config
		# hence we can use A3 paper as it is supported
		mediaNames = self.layout.GetCanonicalMediaNames()
		time.sleep(0.1)
		self.layout.CanonicalMediaName = mediaName
		time.sleep(0.1)

		print(self.layout.StandardScale)
		self.layout.PaperUnits = 1
		#self.layout.UseStandardScale = True
		#self.layout.StandardScale = 34
		# self.layout.CustomScale = 

		self.layoutId 			= str(uuid.uuid4())

	def insert(self, block):

		# insterting associated dwg as block
		block.instance = DOC.PaperSpace.InsertBlock(block.insertionPoint,
													block.path,
													block.scale, 
													block.scale,
													block.scale,
													block.rotation)
		time.sleep(0.1)
		block.ID = block.blockID
		time.sleep(0.1)
		'''
		for attrib in block.instance.GetAttributes():
			if attrib.TagString in block.tags:
				# set attribute in desired block entity from block instance values
				attrib.TextString = block.attrs[attrib.TagString]
		'''
		block.props = block.instance.GetDynamicBlockProperties()
		time.sleep(0.2)
		block.attrs = block.instance.GetAttributes()
		time.sleep(0.2)

		# delete auto-generated layout mesh
		for entity in DOC.PaperSpace:
			name = entity.EntityName
			if name == 'AcDbViewport':
				# this is block created by ACAD and not needed/ Better move this to preprint
				entity.Delete()

	def insert_complex_block(self, complexBlock):

		for block in complexBlock.blocks:

			self.insert(block)

class A3Template(AcadTemplate):
	"""
	ACAD Wrapper for A3 paper form layout"""

	def __init__(self, **kwargs):

		plotConfigName 	= "Adobe PDF"
		mediaName 		= "A3"
		standardScale	= 0

		super().__init__(plotConfigName, mediaName, standardScale, **kwargs)