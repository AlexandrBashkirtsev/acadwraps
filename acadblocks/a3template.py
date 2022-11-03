from pathlib import Path
import os
import win32com.client
import pythoncom

from pyautocad import Autocad, APoint

# SETTINGS
BASE_DIR = Path(__file__).resolve().parent

# connection to AutoCad
ACAD = win32com.client.Dispatch("AutoCAD.Application")
DOC = ACAD.ActiveDocument
ACAD.Visible = True

def ACADPoint(x,y):
	z=0 # z coordinate not used in this project
	return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x,y,z))

class ACADBlock:
	"""
	ACADBlock objects store information about inserted blocks.
	On obj initialization, block inserted in active document from associated dwg file.
	Attributes of block set on initialization."""

	def __init__(self, *args, **kwargs):

		# activate layout in which block will be inserted
		DOC.ActiveLayout = kwargs['layout']
		insertion_point = kwargs['insertion_point']
		insertion_point = ACADPoint(-0.05,-0.05)

		# insterting associated dwg as block
		# x,y,z scales as dm-mm
		# insertion point shift needed because of scale
		self.path = os.path.join(BASE_DIR, "blocks", "title.dwg")



class A3Template:
	"""
	ACAD Wrapper for A3 form block"""

	def __init__(self, id, title, number):

		# make new layout and activate it
		layouts = DOC.Layouts
		names = [l.name for l in layouts]
		layout_name = "Лист" + str(int(names[-1][-1])+1)
		self.layout = layouts.Add(layout_name)
		DOC.ActiveLayout = self.layout

		# check if we can print in PDF
		# if we can, then choose this configuration
		# else, object will not created
		plotDevices = self.layout.GetPlotDeviceNames()
		if "Adobe PDF" in plotDevices:
			self.layout.ConfigName = "Adobe PDF"
		else:
			print("No supported plotter found")
			return

		# at this point we have supported print config
		# hence we can use A3 paper as it is supported
		mediaNames = self.layout.GetCanonicalMediaNames()
		self.layout.CanonicalMediaName = "A3"

		# insterting associated dwg as block
		# x,y,z scales as dm-mm
		# insertion point shift needed because of scale
		self.path = os.path.join(BASE_DIR, "blocks", "title.dwg")
		insertion_point = ACADPoint(-0.05,-0.05)
		self.block = DOC.PaperSpace.InsertBlock(insertion_point, self.path, 0.0393701, 0.0393701, 0.0393701, 0)

		# draw up of inserted blocks
		for entity in DOC.PaperSpace:
			name = entity.EntityName
			if name == 'AcDbViewport':
				# this is block created by ACAD and not needed
				entity.Delete()
			elif name == 'AcDbBlockReference':
				# this is template block
				HasAttributes = entity.HasAttributes
				if HasAttributes:
					for attrib in entity.GetAttributes():
						if attrib.TextString == "title_page_next":
							attrib.TextString = id
							for attrib in entity.GetAttributes():
								if attrib.TagString == "NUMBER":
									attrib.TextString = number
								if attrib.TagString == "TITLE_TEXT":
									attrib.TextString = title
								if attrib.TagString == "TITLE_TEXT_MIRRORED":
									attrib.TextString = title	


list1 = A3Template(id="list1", title="APM.MAG.2021", number="2")
list1 = A3Template(id="list2", title="APM.MAG.2022", number="3")

DOC.Regen(0)
