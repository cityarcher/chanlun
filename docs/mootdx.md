

1、mootdx获取A股日k线数据使用方法：
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')
# 前复权
client.k(symbol="600300", begin="2017-07-03", end="2017-07-10", adjust='qfq')
# 后复权
client.k(symbol="600300", begin="2017-07-03", end="2017-07-10", adjust='hfq')

2、mootdx获取A股分时k线数据使用方法：
# 前复权
client.bars(frequency=9, symbol='000001', start=0, offset=800, adjust='qfq')
# 后复权
client.bars(frequency=9, symbol='000001', start=0, offset=800, adjust='hfq')
frequency的选择有：0标识5分钟k线、1标识15分钟k线、2表示30分钟k线、3表示1小时K线
因为获取的数据是最新日期排在最前面，start=0表示从最新的数据开始，offset=800表示获取800个数据，这个方法一次性可以最多返回800个k线的数据，如果需要返回超过800个数据，需要修改start的数据，分多次获取。如果需要获取1000个数据，则需要client.bars(frequency=9, symbol='000001', start=0, offset=800)获取一次，再client.bars(frequency=9, symbol='000001', start=800, offset=200)再获取一次，然后将两次的数据拼接起来

3、mootdx获取A股指数k线（含日k线和分时k线）数据使用方法：
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')
client.index(frequency=9, symbol='000001', start=0, offset=1000, adjust='qfq')
frequency的选择有：0标识5分钟k线、1标识15分钟k线、2表示30分钟k线、3表示1小时K线
因为获取的数据是最新日期排在最前面，start=0表示从最新的数据开始，offset=800表示获取800个数据，这个方法一次性可以最多返回800个k线的数据，如果需要返回超过800个数据，需要修改start的数据，分多次获取。如果需要获取1000个数据，则需要client.index(frequency=9, symbol='000001', start=0, offset=800)获取一次，再client.index(frequency=9, symbol='000001', start=800, offset=200)再获取一次，然后将两次的数据拼接起来

4、mootdx获取A股etf的k线（含日k线和分时k线）数据使用方法：
client.bars(frequency=2, symbol='588000', start=0, offset=800)
frequency的选择有：0标识5分钟k线、1标识15分钟k线、2表示30分钟k线、3表示1小时K线、9表示日k线、
因为获取的数据是最新日期排在最前面，start=0表示从最新的数据开始，offset=800表示获取800个数据，这个方法一次性可以最多返回800个k线的数据，如果需要返回超过800个数据，需要修改start的数据，分多次获取。如果需要获取1000个数据，则需要client.bars(frequency=9, symbol='000001', start=0, offset=800)获取一次，再client.bars(frequency=9, symbol='000001', start=800, offset=200)再获取一次，然后将两次的数据拼接起来

5、mootdx获取港股的k线（含日k线和分时k线）数据使用方法：
from mootdx.quotes import Quotes
client = Quotes.factory(market='ext')
client.bars(frequency=2,market=71, symbol="09660", start=0, offset=1000, adjust='qfq')
frequency的选择有：0标识5分钟k线、1标识15分钟k线、2表示30分钟k线、3表示1小时K线、9表示日k线、
market有可能为71、31或48
因为获取的数据是最新日期排在最前面，start=0表示从最新的数据开始，offset=700表示获取700个数据，这个方法一次性可以最多返回700个k线的数据，如果需要返回超过700个数据，需要修改start的数据，分多次获取。如果需要获取1000个数据，则需要client.bars(frequency=9,market=71, symbol="09660", start=0, offset=700)获取一次，再client.bars(frequency=9,market=71, symbol="09660", start=700, offset=300)再获取一次，然后将两次的数据拼接起来
