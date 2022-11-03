from pathlib import Path

import os

from acad.acadblocks import DOC, A3Template, A3SecondaryBlock, PLCInputBlock, PLCComplexBlock, PLCFactory, PLCAnalogInputBlock, A3TitleBlockPower

import time

BASE_DIR = Path(__file__).resolve().parent

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# --------------------------------------------------------------------

def get_scheme(chunks, insertionPoint, DIshift, DOshift, AIshift, title, descrShort, doublePower, fillers):

	i = 1
	name = "Лист"

	# insert new list
	template = A3Template(name=name+str(i))
	time.sleep(0.1)

	# activate layout
	DOC.ActiveLayout = template.layout
	time.sleep(2)

	# DOC.Regen(0)

	print("New list created")

	# decorate list with borders
	title_block = A3TitleBlockPower(insertionPoint=(0.0,0.0))
	if not doublePower:

		title_block.path = os.path.join(BASE_DIR, "acadblocks/blocks", "a3title_power_scheme_simple.dwg")

	template.insert(title_block)
	time.sleep(0.1)

	if doublePower:

		title_block.POWER_SOURCE_1 = fillers[0].ID
		title_block.POWER_SOURCE_2 = fillers[1].ID
		title_block.POWER_RESERVE = fillers[2].ID

	else:

		title_block.POWER_SOURCE_1 = fillers[0].ID

	title_block.TITLE_TEXT = title
	title_block.TITLE_TEXT_MIRRORED = title
	title_block.DESCR_SHORT = descrShort
	title_block.NUM = len(chunks)
	

	i += 1

	print("Number of lists: ", len(chunks))

	for chunk in chunks:

		# insert new list
		template = A3Template(name=name+str(i))
		time.sleep(0.1)

		# activate layout
		DOC.ActiveLayout = template.layout
		time.sleep(2)

		# DOC.Regen(0)

		print("New list created")

		# decorate list with borders
		secondary_block = A3SecondaryBlock(insertionPoint=(0.0,0.0))

		template.insert(secondary_block)
		time.sleep(0.1)

		secondary_block.TITLE_TEXT = title
		secondary_block.TITLE_TEXT_MIRRORED = title
		secondary_block.NUMBER = str(i)

		itershift = insertionPoint[1]

		if chunk.iloc[0]['Тип'] == "DI" or chunk.iloc[0]['Тип'] == "DO":

			block_common = PLCInputBlock(insertionPoint=(insertionPoint[0], itershift))

			template.insert(block_common)

			block_common.VISIBILITY = "SIMPLE"
			block_common.POWER_SIMPLE = "-24В"

			if chunk.iloc[0]['Тип'] == "DI":

				block_common.NAME = "Общий входов"
				block_common.NUM = "S/S"
				

			elif chunk.iloc[0]['Тип'] == "DO":

				block_common.NAME = "Общий выходов"
				block_common.NUM = "C"

			itershift = itershift - DIshift

		i += 1

		# DOC.Regen(0)

		#itershift = insertionPoint[1]
		firstBlock = True
		for _, row in chunk.iterrows():

			time.sleep(0.1)

			if row['Тип'] == "DI" or row['Тип'] == "DO":

				block = PLCInputBlock(insertionPoint=(insertionPoint[0], itershift))

			elif row['Тип'] == "AI":

				block = PLCAnalogInputBlock(insertionPoint=(insertionPoint[0], itershift))

			elif row['Тип'] == "DIRECT":

				block = PLCInputBlock(insertionPoint=(insertionPoint[0], itershift)) 

			template.insert(block)

			block.NUM = row['Номер контакта ПЛК']
			block.NAME = row['Наименование цепи']
			
			time.sleep(0.05)

			if row['Тип'] == "DI":

				itershift = itershift - DIshift

				block.VISIBILITY = "INPUT_RELAY"

				block.MARKER_1 = row['Маркировка']
				block.MARKER_2 = row['Маркировка общего']

				block.CLEMM_1 = row['Номер клеммы']
				block.CLEMM_2 = row['Общая клемма']
				block.CONTACT = ""

				if firstBlock:

					block.VISIBILITY = "INPUT_RELAY_FIRST"
					block.POWER = "24В"

			elif row['Тип'] == "DO":

				itershift = itershift - DOshift

				block.VISIBILITY = "OUTPUT_RELAY"

				block.R_CLEMM_1 = row['Номер клеммы']
				block.R_CLEMM_2 = row['Общая клемма']
				block.R_MARKER_1 = row['Маркировка']
				block.R_MARKER_2 = row['Маркировка общего']
				block.MARKER_1 = row['Маркировка контакта реле']
				block.MARKER_2 = row['Маркировка общего контакта реле']
				block.CONTACT = row['Реле']
				

				if firstBlock:

					block.VISIBILITY = "OUTPUT_RELAY_FIRST"
					block.POWER = "24В"

				else:

					block.SHIFT = DOshift

			elif row['Тип'] == "AI":

				itershift = itershift - AIshift

				block.VISIBILITY = row["Подтип"]

				block.V = "V" + row['Номер контакта ПЛК'] + "+"
				block.I = "I" + row['Номер контакта ПЛК'] + "+"
				block.VI = "VI" + row['Номер контакта ПЛК'] + "-"

				if row["Подтип"] == "WIRE_2":

					block.CLEMM_1 = row['Номер клеммы']
					block.CLEMM_2 = row['Клемма питания -']
					block.MARKER_1 = row['Маркировка']
					block.MARKER_2 = row['Маркировка питания -']

				elif row["Подтип"] == "WIRE_3":

					block.CLEMM_3 = row['Номер клеммы']
					block.POWER_1 = row['Клемма питания +']
					block.POWER_2 = row['Клемма питания -']
					block.MARKER_3 = row['Маркировка']
					block.MARKER_4 = row['Маркировка питания +']
					block.MARKER_5 = row['Маркировка питания -']

			elif row['Тип'] == "DIRECT":

				itershift = itershift - DIshift

				block.VISIBILITY = "DIRECT_TO_CLEMM"
				block.MARKER_1 = row['Маркировка']
				block.CLEMM_1 = row['Номер клеммы']



			firstBlock = False
			
			# DOC.Regen(0)

			print("New row block inserted", row['Модуль'] + "|" + row['Номер контакта ПЛК'] + ":", row['Наименование цепи'])

	'''t = A3Template()
	b = A3TitleBlock(insertionPoint=(0.0,0.0),
					TITLE_TEXT="APM.2021",
					NUMBER="42")
	t.insert(b)

	plc = PLCComplexBlock(BlockClass=PLCInputBlock,
			numberOfBlocks=10,
			insertionPoint=(50.0, 240.0),
			shift=12.0)

	t.insert_complex_block(plc)

	initY = 240.0
	shiftY = 12.0
	initName = "ЗЗУ №"
	initNum = "X0."
	initClemm = "X1."'''

	DOC.Regen(0)