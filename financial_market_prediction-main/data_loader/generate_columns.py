from peewee import *
import datetime

# from core.run_time import merge
name = "candlestick_db.db"
db = SqliteDatabase(name)

class BaseModel(Model):
    class Meta:
        database = db

class Coinmarket(BaseModel):
    coin = TextField()
    market = TextField(default="BTC")

class Data(BaseModel):
    coin_data = ForeignKeyField(Coinmarket, backref='candles')
    open = DecimalField(decimal_places=8, auto_round=True)
    high = DecimalField(decimal_places=8, auto_round=True)
    low = DecimalField(decimal_places=8, auto_round=True)
    close = DecimalField(decimal_places=8, auto_round=True)

    shares = DecimalField(decimal_places=8, auto_round=True)
    btc_vol = DecimalField(decimal_places=8, auto_round=True)

    timestamp = BigIntegerField()

# print("!!!")

def generate(coin, market):
    db.connect()
    db.create_tables([Coinmarket, Data])

    new_coin = Coinmarket(coin=coin, market=market)
    new_coin.save()
    return new_coin
