from datetime import date

class Trader:
	def __init__(self, principal, stocks):
		self.principal = principal
		self.stocks = stocks

		self.balance = self.principal
		self.shares = {}
		self.quotes = {}

	def buy(self, quote, shares=None, weight=None):
		if quote is None:
			return

		shares = shares if shares is not None else int(weight * self.balance / quote.close)
		price = quote.close * shares

		self.balance -= price
		self.shares[quote.symbol] = self.shares[quote.symbol] + shares if quote.symbol in self.shares else shares

	def sell(self, quote, shares=None):
		if quote is None or not quote.symbol in self.shares:
			return

		if shares is None:
			shares = self.shares[quote.symbol]

		price = quote.close * shares

		self.balance += price
		self.shares[quote.symbol] -= shares

	def update(self, year=None, month=None, day=None):
		for stock in self.stocks:
			self.quotes[stock.symbol] = stock.get_quotes(year, month, day)[0]

	def get_change(self):
		change = 0

		for share in self.shares:
			change += self.shares[share] * self.quotes[share].close

		return (self.balance + change) - self.principal

	def get_percent_change(self):
		return self.get_change() / self.principal * 100
