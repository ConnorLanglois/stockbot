import json
from stock import sectors, Stock, Quote
from time import sleep

start_date = 1993
end_date = 2017

sleep_time = 0.1

for sector in sectors:
	with open(f'../quotes/{sector}.json', 'w+') as file:
		stock = Stock(sector)
		data = []

		for i in range(start_date, end_date):
			quotes = stock.get_historical('01', '01', i, '01', '01', i + 1)[::-1]
			data += [quote.data for quote in quotes]

			for quote in quotes:
				print(quote.symbol, quote.date)

			sleep(sleep_time)

		file.write(json.dumps(data))
