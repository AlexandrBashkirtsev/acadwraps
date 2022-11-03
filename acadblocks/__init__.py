from pathlib import Path
import os
import win32com.client
import pythoncom
import uuid

# comtypes
'''
import comtypes.client
from comtypes import COMError
from comtypes.client import CreateObject, GetActiveObject

from pyautocad import Autocad
'''

# SETTINGS
BASE_DIR = Path(__file__).resolve().parent

# connection to AutoCad

ACAD = win32com.client.Dispatch("AutoCAD.Application")
DOC = ACAD.ActiveDocument

# ACAD = GetActiveObject("AutoCAD.Application")
# DOC = ACAD.Documents.Items(0)
# DOC = ACAD.ActiveDocument

LAYOUTS = DOC.Layouts
ACAD.Visible = True

from .acadblock import A3SecondaryBlock, PLCInputBlock, PLCAnalogInputBlock, A3TitleBlockPower
from .acadtemplates import A3Template
from .plc import PLCComplexBlock, PLCFactory