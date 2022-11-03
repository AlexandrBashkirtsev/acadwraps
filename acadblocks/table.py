class Table:

	def __init__(self, *args, **kwargs):

		self.rows = kwargs['rows']
		self.cols = kwargs['cols']
		self.insertion_point = kwargs['insertion_point']

	def fill_from_dataframe(self, df):

		pass

table = Table(rows=1,
				cols=1,
				insertion_point=1)