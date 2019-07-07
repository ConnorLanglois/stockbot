import json
from pprint import pprint
from stock import sectors, Quote, Stock
from trader import Trader

stocks = {}

for sector in sectors:
	with open(f'../quotes/{sector}.json', 'r') as file:
		stocks[sector] = Stock(sector, file=file)

with open('../quotes/SPY.json', 'r') as file:
	stocks['SPY'] = Stock('SPY', file=file)

top = []
spy_pc = []
start_year = 2016
end_year = 2016

for year in range(start_year, end_year + 1):
	for month in range(1, 13):
		changes = {}

		for stock in stocks.values():
			year_from = (year - 1) if month < 4 else year
			month_from = (month - 3) % 12 if month != 3 else 12
			day_from = stock.get_quotes(year_from, month_from)[0].date.day
			day_to = stock.get_quotes(year, month)[0].date.day
			pc = stock.get_percent_change(year_from, month_from, day_from, year, month, day_to)

			if stock.symbol != 'SPY':
				changes[stock.symbol] = pc

		sort = sorted(changes, key=lambda key: changes[key].percent_change if changes[key].percent_change is not None else -999999999, reverse=True)[:3]
		top.append([changes[symbol] for symbol in sort])

pprint([[i + 1, quotes[0].symbol, quotes[1].symbol, quotes[2].symbol] for quotes, i in zip(top, range(len(top)))])

trader = Trader(1000, stocks.values())
weights = (0.5, 0.3, 0.2)

count = {sector: [0, 0] for sector in sectors}

print(' '.join(str(quote.percent_change) for quote in spy_pc))

def trade():
	for quotes, i in zip(top, range(len(top))):
		date = [int(c) if c != 'None' else None for c in quotes[0].date_to.split('-')]
		prices = {stock: stocks[stock].get_quote(*date) for stock in stocks}

		year = date[0] - 1 if date[1] < 11 else date[0]
		month = (date[1] - 10) % 12 if date[1] != 10 else 12
		day = date[2]

		average = stocks['SPY'].get_average(year, month, day, date[0], date[1], date[2]).average

		trader.update(*date[:2])

		for stock in stocks:
			trader.sell(prices[stock])

			index = -1

			for quote, j in zip(quotes, range(len(quotes))):
				if quote.symbol == stock:
					index = j

			if index != -1:
				if index == count[stock][0]:
					count[stock][1] += 1
				else:
					count[stock][0] = index
					count[stock][1] = 1
			else:
				count[stock] = [0, 0]

		for quote, k in zip(quotes, range(len(quotes))):
			if count[quote.symbol][1] < 3: # and stocks['SPY'].get_average(date[0], date[1]).average > average:
				trader.buy(prices[quote.symbol], weight=weights[k])

trade()

print(trader.get_percent_change())





def trade1():
	for quotes in top:
		trader.update(quotes[0].date_to)

		for quote, i in zip(quotes, range(0, len(quotes))):
			count[quote.symbol] = count[quote.symbol] + 1 if quote.symbol in count else 1

			if count[quote.symbol] < 3:
				print(quote)
				trader.buy(quote, weight=weights[i])
			else:
				trader.sell(quote)

			for sector in sectors:
				found = False

				for quote in quotes:
					if quote.symbol == sector:
						found = True

				if sector in count and not found:
					del count[sector]

def trade2():
	for quotes in top:
		trader.update(quotes[0].date_to)

		for sector in sectors:
			index = -1

			for quote, i in zip(quotes, range(0, len(quotes))):
				if quote.symbol == sector:
					index = i

					break

			if index != -1 and count[quote.symbol] < 3:
				count[quote.symbol] = count[quote.symbol] + 1

				trader.sell(quote)
				trader.buy(quote, weight=weights[index])
			else:
				count[quote.symbol] = 0

				trader.sell(quote)

			print(count)
