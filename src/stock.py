import json
from datetime import date
from time import sleep
from urllib import parse, request, error

sectors = ('XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY') # 'XLRE', 

class Stock:
	def __init__(self, symbol, quotes=[], file=None):
		self.symbol = symbol
		self.quotes = quotes

		if file is not None:
			data = json.loads(file.read())
			quotes = [Quote(quote) for quote in data]
			self.quotes = quotes

	def get_historical(self, start_day, start_month, start_year, end_day, end_month, end_year):
		def get(query, count=0):
			try:
				data = json.loads(request.urlopen(query).read())['query']['results']['quote']
			except error.HTTPError:
				sleep(10)
				
				if count < 5:
					data = get(query, count=count+1)
				else:
					raise error.HTTPError()
			except TypeError:
				data = ''

			return data

		query = 'http://query.yahooapis.com/v1/public/yql?q=' + parse.quote(f'''select * from yahoo.finance.historicaldata where symbol = "{self.symbol}"
																				and startDate = "{start_year}-{start_month}-{start_day}"
																				and endDate = "{end_year}-{end_month}-{end_day}"
																				&format=json&env=store://datatables.org/alltableswithkeys''', '/*=&')
		data = get(query)
		quotes = [Quote(quote) for quote in data]

		return quotes

	def get_percent_change(self, start_year=None, start_month=None, start_day=None, end_year=None, end_month=None, end_day=None):
		quote = self.get_change(start_year, start_month, start_day, end_year, end_month, end_day)

		quote.percent_change = quote.change / quote.average_from if quote.change is not None else None

		return quote

	def get_change(self, start_year=None, start_month=None, start_day=None, end_year=None, end_month=None, end_day=None):
		average_from = self.get_average(start_year, start_month, start_day).average
		average_to = self.get_average(end_year, end_month, end_day).average
		change = average_to - average_from if average_from is not None and average_to is not None else None

		return Quote({
			'Symbol': self.symbol,
			'date_from': f'{start_year}-{start_month}-{start_day}',
			'date_to': f'{end_year}-{end_month}-{end_day}',
			'average_from': average_from,
			'average_to': average_to,
			'price': average_to,
			'change': change
			})

	def get_average(self, start_year=None, start_month=None, start_day=None, end_year=None, end_month=None, end_day=None):
		quotes = self.get_quotes(start_year, start_month, start_day, end_year, end_month, end_day)
		average = 0 if len(quotes) > 0 else None

		for quote in quotes:
			average += quote.close / len(quotes)

		return Quote({
			'Symbol': self.symbol,
			'date_from': f'{start_year}-{start_month}-{start_day}',
			'date_to': f'{end_year}-{end_month}-{end_day}',
			'average': average
			})

	def get_quote(self, year, month, day):
		quotes = self.get_quotes(year, month, day)

		return quotes[0] if len(quotes) == 1 else None

	def get_quotes(self, start_year=None, start_month=None, start_day=None, end_year=None, end_month=None, end_day=None):
		quotes = []

		if start_year is None and start_month is None and start_day is None:
			quotes = self.quotes
		elif end_year is None:
			for quote in self.quotes:
				if ((quote.date.year == start_year or start_year is None) and
					(quote.date.month == start_month or start_month is None) and
					(quote.date.day == start_day or start_day is None)):

					quotes.append(quote)
		else:
			date1 = date(start_year, start_month, start_day)
			date2 = date(end_year, end_month, end_day)

			quotes = [quote for quote in self.quotes if quote.date.toordinal() >= date1.toordinal() and quote.date.toordinal() <= date2.toordinal()]

		return quotes

	def __str__(self):
		return self.symbol + f'({self.quotes[0].date} - {self.quotes[-1].date})\n\n' + ''.join(str(quote) for quote in self.quotes)

class Quote:
	def __init__(self, data):
		self.data = data

		def nfloat(n):
			return float(n) if n != None else None

		self.symbol = self.data.get('Symbol')
		self.date = self.data.get('Date')
		self.open = nfloat(self.data.get('Open'))
		self.high = nfloat(self.data.get('High'))
		self.low = nfloat(self.data.get('Low'))
		self.close = nfloat(self.data.get('Close'))
		self.volume = nfloat(self.data.get('Volume'))
		self.adj_close = nfloat(self.data.get('Adj_Close'))
		self.change = self.data.get('change')
		self.average = self.data.get('average')
		self.date_from = self.data.get('date_from')
		self.date_to = self.data.get('date_to')
		self.average_from = self.data.get('average_from')
		self.average_to = self.data.get('average_to')
		self.percent_change = self.data.get('percent_change')
		self.price = (self.open + self.close) / 2 if self.open is not None and self.close is not None else self.data.get('price')

		if self.date is not None:
			date_comps = [int(c) for c in self.date.split('-')]
			self.date = date(date_comps[0], date_comps[1], date_comps[2])

	def __str__(self):
		return (f'{self.symbol} ({self.date}):\n'
				f'\tAdj_Close - {self.adj_close},\n'
				f'\tClose - {self.close},\n'
				f'\tHigh - {self.high},\n'
				f'\tLow - {self.low},\n'
				f'\tOpen - {self.open},\n'
				f'\tVolume - {self.volume}\n'
				f'\tChange - {self.change}\n'
				f'\tAverage - {self.average}\n'
				f'\tPrice - {self.price}\n'
				f'\tDate From - {self.date_from}\n'
				f'\tDate To - {self.date_to}\n'
				f'\tAverage From - {self.average_from}\n'
				f'\tAverage To - {self.average_to}\n'
				f'\tPercent Change - {self.percent_change}\n\n')
