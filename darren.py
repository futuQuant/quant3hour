#encoding:gbk
import datetime
import requests
import json
import pandas as pd

account = '1678060727'
basket_name = 'basket_test'
money = 10000000
order_status = {}

def init(ContextInfo):
 # 设置定时器，历史时间表示会在一次间隔时间后开始调用回调函数 比如本例中 5秒后会后第一次触发myHandlebar调用 之后五秒触发一次
 ContextInfo.run_time("myHandlebar","5nSecond","2023-08-01 09:20:00")

def getCode(symbol):
 suffix = '.SZ' if symbol.startswith("00") or symbol.startswith("30") else '.SH'
 return symbol + suffix

def getLotSize(symbol,quantity):
 return int(quantity) if symbol.startswith("688") else int(quantity//100)*100

def myHandlebar(ContextInfo):
 global order_status
 file_date = datetime.datetime.now().strftime("%Y-%m-%d")
 if file_date not in order_status:
  filepos = pd.read_csv('C:/Users/WikiFX/Desktop/trade/fileorder.csv',dtype={'symbol':str})
  res = {'code':200}
  detail = []
  for i in range(len(filepos)):
      detail.append({'symbol':filepos.iloc[i]['symbol'], 'targetWeight':filepos.iloc[i]['weight'],'tradeDate':datetime.datetime.now().date().strftime('%Y-%m-%d')})
  res['detail'] = detail
  #url = 'http://121.5.218.235/api/trade/recommend?date=' + file_date
  #requests.packages.urllib3.disable_warnings()
  #response = requests.get(url, headers={
   #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
   #'cache-control': 'no-cache',
   #'Referer': 'https://stock.xueqiu.com',
   #'x-token':'MIIBIjAqhkiG9w0B'
  #}, verify=False)
  #res = json.loads(response.text)
  if res['code'] == 200:
    # 当前持仓查询
   position_info = get_trade_detail_data(account, 'stock', 'position')
   positions = {}
   #print(dir(position_info[0]))
   last_prices = {}
   targets = {}
   codes = set()
   for i in position_info:
    symbol = getCode(i.m_strInstrumentID)
    codes.add(symbol)
    positions[symbol] = i.m_nVolume

   #print(positions)
   stocks = []
   csv_datas = []
   for stock in res['detail']:
    symbol = getCode(stock['symbol'])
    targets[symbol] = float(stock['targetWeight'])
    codes.add(symbol)

   ticks=ContextInfo.get_full_tick(list(codes))
   if len(ticks) > 0:
    #print(list(codes),ticks)
    for code, tick in ticks.items():
     last_prices[code] = tick['lastPrice']

    #print('tick',len(last_prices),last_prices)
    for symbol in codes:
     quantity = 0
     if symbol in last_prices:
      if symbol in positions:
       if symbol in targets:
        target_quantity = getLotSize(symbol,targets[symbol]*money/last_prices[symbol])
        quantity = target_quantity - positions[symbol]
        optType = 23 if quantity > 0 else 24
       else:
        target_quantity = positions[symbol]
        quantity = target_quantity
        optType = 24
      elif symbol in targets:
       optType = 23
       # 不是除0的问题，是那时候行情没推送来
       #if last_prices[symbol]==0:
          #print(symbol)
       target_quantity = getLotSize(symbol,targets[symbol]*money/last_prices[symbol])
       quantity = target_quantity
      #print(stock['symbol'],suffix,quantity)
      if quantity != 0:
       data = {
        "stock":symbol,
        "quantity":abs(quantity),
        "weight": 0,
        "optType":optType
       }
       stocks.append(data)
       data['target_quantity'] = target_quantity
       data['position_quantity'] = positions.get(symbol,0)
       data['last_price'] = last_prices.get(symbol,'')
       csv_datas.append(data)
     else:
      print(symbol,'取不到行情')

    #print(stocks)
    #basket={'name': 'basket_test', 'stocks': [{'stock': '000029.SZ', 'weight': 1, 'quantity': 0, 'optType': 24}, {'stock': '000039.SZ', 'weight': 1, 'quantity': 0, 'optType': 23}, {'stock': '000062.SZ', 'weight': 1, 'quantity': 0, 'optType': 23}]}
    set_basket({'name': basket_name, 'stocks': stocks});
    basket=get_basket(basket_name);
    print(basket);
    pd.DataFrame(csv_datas).sort_values('stock').to_csv('history/'+file_date + '.csv', index=False, header=True,
    columns=['stock', 'quantity', 'weight', 'optType','last_price','target_quantity','position_quantity'])
    
    #userparam = {
     #"OrderType": 1,
     #"SuperPriceType":0,
     #"SuperPriceRate":0,
     #"VolumeType":10,
     #"VolumeRate":1,
     #"SingleNumMin":200,
     #"SingleNumMax":10000,
     #"ValidTimeType": 0,
     #"ValidTimeElapse":7200,
     #"MaxOrderCount":20
    #};
    #algo_passorder(35,2102,account,basket_name,5,-1,money,file_date,2,file_date,userparam,ContextInfo);
    #order_status[file_date] = len(ticks)
    #smart_algo_passorder(23,1101,account,'000001.SZ',5,-1,50000,"strageName",1,"remark","TWAP",20,0,0,'09:30:00','14:00:00',ContextInfo)
    #smart_algo_passorder(35,1101,account,basket_name,5,-1,money,"strageName",1,"remark","VWAP",20,200,6,"09:35:00","14:00:00",0,ContextInfo)
    print('order_proceed');
 pass