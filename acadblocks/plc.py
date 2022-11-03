from . import BASE_DIR, DOC, PLCInputBlock
import os
import pandas as pd
import copy
import math

pd.options.mode.chained_assignment = None  # default='warn'

def xlsflt_to_str(value):

	return str(value)[:-2]

class PLCFactory:

	def __init__(self, path, chapters):

		# PLC processor and modules set
		self.stack = []

		self.processor = None
		self.modules = []

		# read scheme configuration file
		df = pd.read_excel(path)
		self.specification = pd.read_excel(path, sheet_name="Лист2")

		# get name and description
		self.title = df.iloc[0]['Заголовок']
		self.descrShort = df.iloc[0]['Описание']
		self.doublePower = df.iloc[0]['Резервное питание']

		# count clemms
		self.count_clemms(df)

		# clean dataframe
		df = df[["Номер клеммника",
				"Номер клеммы",
				"Наименование цепи",
				"Назначение",
				"Маркировка",
				"Общий",
				"Общая клемма",
				"Раздел",
				"Тип",
				"Маркировка общего",
				"Маркировка контакта реле",
				"Маркировка общего контакта реле",
				"Подтип",
				"Клемма питания +",
				"Клемма питания -",
				"Маркировка питания +",
				"Маркировка питания -"]]

		# init chapters to implement
		self.chapters = []

		for chapter in chapters:

			df_chapter = df[df['Раздел'] == chapter]

			df_chapter['Номер клеммы'] = df_chapter.apply(self.change_clemm, axis=1)
			df_chapter['Общая клемма'] = df_chapter.apply(self.change_common_clemm, axis=1)
			df_chapter['Клемма питания +'] = df_chapter.apply(self.change_power_clemm_1, axis=1)
			df_chapter['Клемма питания -'] = df_chapter.apply(self.change_power_clemm_2, axis=1)

			if df_chapter.iloc[0]['Тип'] == "DI" or df_chapter.iloc[0]['Тип'] == "DO":
				df_chapter = df_chapter[df_chapter['Общая клемма'].notna()]
			elif df_chapter.iloc[0]['Тип'] == "AI":
				df_chapter = df_chapter[df_chapter['Подтип'].notna()]

			df_chapter = df_chapter[["Номер клеммы",
									"Наименование цепи",
									"Назначение",
									"Маркировка",
									"Общий",
									"Общая клемма",
									"Тип",
									"Маркировка общего",
									"Маркировка контакта реле",
									"Маркировка общего контакта реле",
									"Подтип",
									"Клемма питания +",
									"Клемма питания -",
									"Маркировка питания +",
									"Маркировка питания -"]]

			self.chapters.append(df_chapter)

			self.relay = 1

	def change_clemm(self, row):

		return "X" + xlsflt_to_str(row['Номер клеммника']) + "." + xlsflt_to_str(row['Номер клеммы'])

	def change_common_clemm(self, row):

		if not pd.isna(row['Общая клемма']):
			return "X" + xlsflt_to_str(row['Номер клеммника']) + "." + xlsflt_to_str(row['Общая клемма'])
		else:
			return row['Общая клемма']

	def change_power_clemm_1(self, row):

		if not pd.isna(row['Клемма питания +']):
			return "X" + xlsflt_to_str(row['Номер клеммника']) + "." + xlsflt_to_str(row['Клемма питания +'])
		else:
			return row['Клемма питания +']

	def change_power_clemm_2(self, row):

		if not pd.isna(row['Клемма питания -']):
			return "X" + xlsflt_to_str(row['Номер клеммника']) + "." + xlsflt_to_str(row['Клемма питания -'])
		else:
			return row['Клемма питания -']

	def append_module(self, contactType):

		for module in self.modules:

			if module.haveType(contactType):

				self.stack.append(copy.deepcopy(module))
				self.stack[-1].ID = self.stack[-1].ID + str(len(self.stack))

	def choose_contact(self, row):

		contactType = row['Тип']
		commentType = row['Подтип']

		assigned = False

		if contactType == "DIRECT":

			return pd.Series(["Direct contact", "No module"])

		for mod in self.stack:

			if mod.haveFreeType(contactType):

				contact = mod.assing_contact(contactType)
				ID = mod.ID
				assigned = True

				return pd.Series([contact, ID])

		if not assigned:

			self.append_module(contactType)
			contact = self.stack[-1].assing_contact(contactType)
			ID = self.stack[-1].ID

			return pd.Series([contact, ID])

	def choose_relay(self, row):

		if row["Тип"] == "DO":

			relay = "K" + str(self.relay)
			self.relay += 1

			return relay

	def split_chapter(self, chapter, chunkSize = 10): 
		chunks = list()
		# numberChunks = len(chapter) // chunkSize + 1
		numberChunks = math.ceil(len(chapter) / chunkSize)
		for i in range(numberChunks):
			chunks.append(chapter[i*chunkSize:(i+1)*chunkSize])
		return chunks

	def get_plc_config(self, modulesConfig):

		"""
		returns plc configuration
		modules: plc processor and IO modules to choose from"""

		# get processor
		self.processor = PLCModule(modulesConfig['processor'])
		self.processor.ID = self.processor.ID + "1"

		# get available modules
		self.modules = [PLCModule(module) for module in modulesConfig['modules']]

		# get acad block classes for drawing
		self.complexBlockClass = modulesConfig['complexBlockClass']
		self.inputBlockClass = modulesConfig['inputBlockClass']

		# get split size: number of blocks per autocad sheet
		self.splitSizeDI = modulesConfig['splitSizeDI']
		self.splitSizeDO = modulesConfig['splitSizeDO']
		self.splitSizeAI = modulesConfig['splitSizeAI']

		# init modules stack
		self.stack.append(self.processor)

		# check needed inputs
		for chapter in self.chapters:

			chapter[['Номер контакта ПЛК', 'Модуль']] = chapter.apply(self.choose_contact, axis=1)
			chapter['Реле'] = chapter.apply(self.choose_relay, axis=1)

		# print(self.chapters)

		# blockChapters = []

		chapterChunks = []

		for chapter in self.chapters:

			modulesSplitted = [sub_df for _, sub_df in chapter.groupby("Модуль")]

			for module in modulesSplitted:

				if module.iloc[0]['Тип'] == "DI":

					splitSize = self.splitSizeDI

				elif module.iloc[0]['Тип'] == "DO":

					splitSize = self.splitSizeDO

				elif module.iloc[0]['Тип'] == "AI":

					splitSize = self.splitSizeAI

				else:

					splitSize = self.splitSizeDI

				chunks = self.split_chapter(module, chunkSize=splitSize)

				for chunk in chunks:

					chapterChunks.append(chunk)

			blocks = []
			"""
			for _, row in chapter.iterrows():

				
				
				plc = self.complexBlockClass(BlockClass=self.inputBlockClass,
											numberOfBlocks=self.splitSize,
											insertionPoint=(50.0, 240.0),
											shift=12.0)
				
			"""
		return chapterChunks

	def append_filler_modules(self, row):
		
		if row["Заполнить"]:

			if row["Обозначение"] == "U":
				for i in range(0, int(row["Количество"])):
					self.stack.append(FillerModule(row["Наименование"]))
					self.stack[-1].ID = self.stack[-1].ID + str(len(self.stack))

			elif row["Обозначение"] == "K":

				row["Количество"] = self.relay

				if self.relay > 1:

					row["Обозначение"] = "K1 - K" + str(int(self.relay))
				else:
					row["Обозначение"] = "K1"


			elif row["Обозначение"] == "X":

				row["Обозначение"] = self.clemms_id
				row["Количество"] = self.clemms_number

		return row

	def count_module(self, module):

		count = 0

		for compare in self.stack:

			if compare.name == module.name:

				count += 1

		return count

	def count_clemms(self, df):

		df = df[df['Номер клеммы'].notna()]

		df = [sub_df for _, sub_df in df.groupby("Номер клеммника")]

		self.clemms_number = 0
		ids = []
		for chapter in df:

			self.clemms_number += len(chapter)
			ids.append("X" + str(int(chapter.iloc[0]['Номер клеммника'])))

		if len(ids) > 1:

			self.clemms_id = ids[0] + " - " + ids[-1]

		else:

			self.clemms_id = ids[0]


	def get_similar_IDs(self, module):

		ids = []

		for compare in self.stack:

			if compare.name == module.name:

				ids.append(compare.ID)

		if len(ids) > 1:
			ids = ids[0] + " - " + ids[-1]
		else:
			ids = ids[0]

		return ids

	def get_specification(self):

		self.specification = self.specification.apply(self.append_filler_modules, axis=1)
		self.specification = self.specification[self.specification["Остаток"] != True]

		for m in self.stack:

			count = self.count_module(m)
			ids = self.get_similar_IDs(m)

			row = pd.DataFrame([[ids, m.name, count, None, None, None]], columns=self.specification.columns)
			self.specification = self.specification.append(row)

		self.specification = self.specification.drop_duplicates(["Наименование"])

		return self.specification

	def get_filler_modules(self):

		fillers = []

		for m in self.stack:

			if isinstance(m, FillerModule):

				fillers.append(m)

		return fillers


class PLCComplexBlock:

	"""
	definition for abstract PLC class.
	Purpose of class is to link acad blocks to table data"""

	def __init__(self, BlockClass, numberOfBlocks, insertionPoint, shift, *args, **kwargs):

		self.blocks = []

		self.block_shift = 0.0

		for i in range(0, numberOfBlocks):

			block = BlockClass(insertionPoint=(insertionPoint[0], insertionPoint[1] - block_shift))
			block_shift = block_shift + shift + block.height
			self.blocks.append(block)

	def append(self, block):

			block_shift = block_shift + shift + block.height
			self.blocks.append(block)

class PLCModule:

	def __init__(self, filename):

		self.path = os.path.join(BASE_DIR, "plc", filename + ".xlsx")	# path to module configuration file

		df = pd.read_excel(self.path)

		self.name = df['name'].tolist()[0]
		self.ID = "U"
		self.number = 0

		self.DI = df['DI'].dropna().tolist()
		self.DO = df['DO'].dropna().tolist()
		self.AI = df['AI'].dropna().tolist()
		self.AO = df['AO'].dropna().tolist()

		self.haveDI = (len(self.DI) > 0)
		self.haveDO = (len(self.DO) > 0)
		self.haveAI = (len(self.AI) > 0)
		self.haveAO = (len(self.AO) > 0)


	def haveFreeDI(self):

		return (len(self.DI) > 0)

	def haveFreeDO(self):

		return (len(self.DO) > 0)

	def haveFreeAI(self):

		return (len(self.AI) > 0)

	def haveFreeAO(self):

		return (len(self.AO) > 0)

	def haveType(self, contactType):

		if contactType == "DI":
			return self.haveDI
		elif contactType == "DO":
			return self.haveDO
		elif contactType == "AI":
			return self.haveAI
		elif contactType == "AO":
			return self.haveAO

	def haveFreeType(self, contactType):

		if contactType == "DI":
			return self.haveFreeDI()
		elif contactType == "DO":
			return self.haveFreeDO()
		elif contactType == "AI":
			return self.haveFreeAI()
		elif contactType == "AO":
			return self.haveFreeAO()

	def assing_contact(self, contactType):

		if contactType == "DI":
			return self.DI.pop(0)
		elif contactType == "DO":
			return self.DO.pop(0)
		elif contactType == "AI":
			return str(self.AI.pop(0))
		elif contactType == "AO":
			return self.DO.pop(0)

class FillerModule:


	def __init__(self, name):

		self.ID = "U"
		self.name = name
		self.number = 0