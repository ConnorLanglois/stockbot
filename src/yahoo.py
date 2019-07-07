from pprint import pprint
from yahoo_finance import Share

aapl = Share('XLK')
data = aapl.get_historical('2016-02-01', '2017-01-01')

pprint(data)
