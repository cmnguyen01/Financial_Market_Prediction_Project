# from .generate_columns import generate
import json
from urllib.request import urlopen

# generate()

def kline_api(symbol, interval, start_point=None, end_point=None):
    if(end_point == None and start_point == None):
        base_url = "https://api.binance.com/api/v1/klines?symbol={}&interval={}".format(symbol, interval)
    elif(end_point != None and start_point == None):
        base_url = "https://api.binance.com/api/v1/klines?symbol={}&interval={}&endTime={}".format(symbol, interval, end_point)
    elif(end_point == None and start_point != None):
        base_url = "https://api.binance.com/api/v1/klines?symbol={}&interval={}&startTime={}".format(symbol, interval, start_point)
        print(base_url)
    request = urlopen(base_url).read()
    data = json.loads(request)
    if(end_point == None and start_point == None):
        return data
    elif(end_point != None and start_point == None):
        return data[:-1]
    elif(start_point != None and end_point == None):
        return data[1:]
