import time
from multiprocessing import Pool
import json
from urllib.request import urlopen
from data_loader.generate_columns import generate, Data, Coinmarket, db
from datetime import datetime

def query_coin(coin, market):
    query = Coinmarket.select().where(Coinmarket.coin == coin, Coinmarket.market == market)
    try:
        return query[0]
    except IndexError:
        # Coin doesn't exist
        return False

def create_coin(coin, market):
    new_coin = Coinmarket(coin=coin, market=market)
    new_coin.save()
    return new_coin

def kline_api(symbol, interval, start_point=None, end_point=None):
    # print(symbol)

    if(end_point == None and start_point == None):
        base_url = "https://api.binance.com/api/v1/klines?symbol={}&interval={}".format(symbol, interval)
    elif(end_point != None and start_point == None):
        base_url = "https://api.binance.com/api/v1/klines?symbol={}&interval={}&endTime={}".format(symbol, interval, end_point)
    elif(end_point == None and start_point != None):
        base_url = "https://api.binance.com/api/v1/klines?symbol={}&interval={}&startTime={}".format(symbol, interval, start_point)
        # print(base_url
    request = urlopen(base_url).read()
    data = json.loads(request)

    return data


def calculateRange(start):
    # start: in binance unix epoch time * 1000
    # Binance returns data from start to end - 1 second
    # This function returns the next start value

    '''
        Start candle open : unix time
        Last candle close : unix time + 30000000
    '''
    return start + 30000000

def createWork(batch_size, market, interval, start):
    # Generates some templates to feed into kline api function
    # market : str
    # interval : str
    # start : int
    work_array = []
    for i in range(batch_size):
        work_array.append((market, interval, start))
        start = calculateRange(start)

    return work_array

def lastCandle(coin, market):
    candle = Data.select().join(Coinmarket).where(Coinmarket.coin == coin, Coinmarket.market == market).order_by(Data.timestamp.desc()).first()
    if(candle == None):
        return None
    else:
        return candle

def delete_duplicates(coin, market):
    candles = Data.select().join(Coinmarket).where(Coinmarket.coin == coin, Coinmarket.market == market).order_by(Data.timestamp.asc()).execute()
    stamps = [i.timestamp for i in candles]
    duplicates = list(set([x for x in stamps if stamps.count(x) > 1]))

    if(len(duplicates) == 0):
        print("No duplicates found")
        return False
    for i in duplicates:
        query = Data.select().where(Data.timestamp == i).join(Coinmarket).where(Coinmarket.coin == coin, Coinmarket.market == market).order_by(Data.timestamp.asc()).execute()

        if(len(query) > 1):
            print("[!] Deleted {}".format(query[0].id))
            query[0].delete_instance()
    return True

if __name__ == "__main__":

    # print(lastCandle("ETH", "USDT").timestamp)
    # generate("XMR", "USDT")

    # Deletes duplicates in database
    # delete_duplicates("XMR", "USDT")

    # Checks the spacing inbetween each candle timestamp, normal = 6000 == 6 second
    # candles = Data.select().join(Coinmarket).where(Coinmarket.coin == "XMR", Coinmarket.market == "USDT").order_by(Data.timestamp.asc()).execute()
    # for i in range(1, len(candles)):
    #     try:
    #         assert (candles[i].timestamp - candles[i-1].timestamp) == 60000
    #     except Exception as e:
    #         print(i, (candles[i].timestamp - candles[i-1].timestamp))

    # Coin
    coin = "ETH"
    market = "USDT"
    symbol = coin + market



    start_unix = lastCandle(coin, market)

    if(start_unix == None):
        start_unix = 1585614634000 # ~2 years ago
    else:
        start_unix = start_unix.timestamp + 1000

    ts = int(start_unix/1000)
    dt = datetime.fromtimestamp(ts).strftime("%m/%d/%Y %H:%M:%S")

    print(f" ------- Start Time: {dt} ------- ")

    # Workers = pool size
    # batch size = how many windows of data to create, also equals 500 one minute candles
    workers = 20

    # ~3 / day  * 30 / month
    batch_size = 3 * 30 * 12

    starttime = time.time()

    pool = Pool(workers)

    work = createWork(batch_size, symbol, "1m", start_unix)
    data = pool.starmap(kline_api, work)

    pool.close()
    pool.join()


    # print(data)
    # assert 1 == 0

    data = sorted(data, key=lambda x: x[0][0])

    coin_model = query_coin(coin, market)

    for batch in data:
        # Convert data
        newData = []
        for i in batch:
            newData.append((coin_model, int(i[0]), float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[7]), float(i[5]) ))

        # Insert each batch into database
        with db.atomic():
            Data.insert_many(newData, fields=[Data.coin_data, Data.timestamp, Data.open, Data.high, Data.low, Data.close, Data.btc_vol, Data.shares]).execute()
        # print("Success")

    print(f" ------- Run Time: {time.time() - starttime} ------- ")

    # # print(data[0][-1][0] - data[0][0][0])
    # n = [i[0][0] for i in data]
    # for i in range(1, len(n)):
    #     print(n[i]-n[i-1])
