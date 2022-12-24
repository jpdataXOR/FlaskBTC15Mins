from ccxt import kraken
from datetime import datetime, timedelta
from flask import Flask, render_template
import pytz
import requests
import binance
from enum import Enum

# Create a Flask app
app = Flask(__name__)


@app.route('/')
def index():
  # Create a Kraken client
  client = kraken()

  # Set the timeframe to 15 minutes
  timeframe = '15m'

  # Get the OHLC data for BTC
  ohlcv = client.fetch_ohlcv('BTC/USD', limit=30, timeframe=timeframe)
  #ohlcv = ohlcv[::-1]
  #print(ohlcv);
  #print(ohlc_to_heiken_ashi(ohlcv))
  trendChanges = detect_trend_change(ohlc_to_heiken_ashi(ohlcv),
                                     num_prev_candles=3)
  trendChanges = trendChanges[::-1]
  #trade(BuySell.NONE)

  # Calculate the percentage change and "Up/Down" value for each candle

  return render_template('index.html', trendChanges=trendChanges)


###########################################


def ohlc_to_heiken_ashi(ohlc_array):
  # Initialize the Heiken Ashi array with the same shape as the OHLC array
  heiken_ashi_array = (ohlc_array)

  # Set the open price for the first candle in the Heiken Ashi array

  # Set the timestamp, open, high, low, and close prices, and volume data for each subsequent candle in the Heiken Ashi array
  for i in range(1, len(ohlc_array)):

    heiken_ashi_array[0][1] = (ohlc_array[i - 1][1] + ohlc_array[i - 1][4]) / 2

    heiken_ashi_array[i][4] = (ohlc_array[i][1] + ohlc_array[i][2] +
                               ohlc_array[i][3] + ohlc_array[i][4]) / 4

  # Return the Heiken Ashi array
  return heiken_ashi_array


def detect_trend_change(ohlc_array, num_prev_candles=2):
  # Initialize the trend variable with the value of the first candle's close price
  trendPrint = []
  trend = ohlc_array[0][4]

  # Get the time zone for AEST
  timezone = pytz.timezone("Australia/Sydney")

  # Iterate over the candles in the OHLC array
  for i in range(1, len(ohlc_array) - 1):
    # Check if the current candle's close price is higher than the average of the previous num_prev_candles candles' close prices

    if ohlc_array[i][4] > sum(
      [ohlc_array[i - j][4]
       for j in range(1, num_prev_candles + 1)]) / num_prev_candles:
      # If the current candle's close price is higher than the average of the previous num_prev_candles candles' close prices,
      # check if the current trend is a downtrend
      if trend < 0:
        # If the current trend is a downtrend, print a message indicating that the trend has changed
        timestamp = ohlc_array[i][0]
        time = datetime.fromtimestamp(timestamp / 1000, tz=timezone)
        print(f"Trend changed at {time} to an uptrend")
        trendPrint.append(f"Trend changed at {time} to an uptrend")
        if i == len(ohlc_array) - 2:
          trendPrint.append("IFTTT")
          send_ifttt_alert(f"Trend changed at {time} to an uptrend")
          #trade(BuySell.BUY)

      # Set the trend to an uptrend
      trend = 1
    # If the current candle's close price is lower than the average of the previous num_prev_candles candles' close prices,
    # check if the current trend is an uptrend
    elif ohlc_array[i][4] < sum(
      [ohlc_array[i - j][4]
       for j in range(1, num_prev_candles + 1)]) / num_prev_candles:
      if trend > 0:
        # If the current trend is an uptrend, print a message indicating that the trend has changed
        timestamp = ohlc_array[i][0]
        time = datetime.fromtimestamp(timestamp / 1000, tz=timezone)
        print(f"Trend changed at {time} to a downtrend")
        trendPrint.append(f"Trend changed at {time} to a downtrend")
        if i == len(ohlc_array) - 2:
          trendPrint.append("IFTTT")
          send_ifttt_alert(f"Trend changed at {time} to a downtrend")
          #trade(BuySell.SELL)

      # Set the trend to a downtrend
      trend = -1
    # Check if the current candle is the last candle in the array

  return trendPrint


def send_ifttt_alert(message):
  # Set the IFTTT webhook URL
  ifttt_webhook_url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

  # Set the event name and your IFTTT key This is Fror IFTTT alert
  event_name = "REPLIT_WEBHOOK"
  ifttt_key = "Z8c3ce6FYDdpqcBWVwJy4"

  # Format the webhook URL with the event name and IFTTT key
  url = ifttt_webhook_url.format(event=event_name, key=ifttt_key)

  # Set the payload for the IFTTT alert
  payload = {"value1": message}

  # Send the IFTTT alert
  requests.post(url, json=payload)

  #This was added for  testing if IFTT alerts are intact
  ifttt_key_sheets = "onjDOQAzxSIr9HH9EkxxdmcEzjNebeauy3gBN9Evv2t"

  # Format the webhook URL with the event name and IFTTT key
  url = ifttt_webhook_url.format(event=event_name, key=ifttt_key_sheets)

  # Set the payload for the IFTTT alert
  payload = {"value1": message}

  # Send the IFTTT alert for Google sheets
  requests.post(url, json=payload)


######################################


class BuySell(Enum):
  BUY = "buy"
  SELL = "sell"
  NONE = "none"


# Set up connection to Binance testnet


def trade(buy_sell, amount=1000):
  client = binance.Client(
    api_key="tDYa8qZ9oBRORUsbYlrFjxRXzx1uo3v4GAkBNrCqPN4bRPJkh4VUGBMyrl2AbTJR",
    api_secret=
    "oR72Fcf82YyaGvJicOeW9pI7Gy98wevF2jZf9h4jZY7eZbH2a6s1S2bSBGJOGfRF",
    testnet=True)
  # Close any previous positions

  client.futures_close_all_position()

  # Set leverage to 10x
  client.futures_change_leverage(10)

  # Check if we are buying or selling
  if buy_sell == BuySell.BUY:
    # Place a buy order for the specified amount
    client.futures_place_order(symbol="BTCUSDT",
                               side="BUY",
                               type="MARKET",
                               quantity=amount)
  elif buy_sell == BuySell.SELL:
    # Place a sell order for the specified amount
    client.futures_place_order(symbol="BTCUSDT",
                               side="SELL",
                               type="MARKET",
                               quantity=amount)
  # Retrieve account information
  account_info = client.get_account()

  # Print total balance of your wallet
  print("Total balance in your wallet:", account_info["totalBalance"])


app.run(host='0.0.0.0', port=81)
########################################
