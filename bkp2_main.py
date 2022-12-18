from ccxt import kraken
import numpy as np
from datetime import datetime
from flask import Flask, render_template
import pytz
import requests

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
  print(detect_trend_change(ohlc_to_heiken_ashi(ohlcv)))
  # Calculate the percentage change and "Up/Down" value for each candle
  candles = []
  previous_close = ohlcv[0][4]
  for candle in ohlcv[1::]:
    # Get the open, high, low, and close values from the candle data
    timestamp = candle[0]
    open_price = candle[1]
    high_price = candle[2]
    low_price = candle[3]
    close_price = candle[4]
    percent_change = (close_price - previous_close) / previous_close * 100
    up_down = "Up" if close_price >= previous_close else "Down"
    # Convert the timestamp value to a date/time object
    if isinstance(timestamp, int):
      timestamp /= 1000
      date_time = datetime.fromtimestamp(timestamp)
    else:
      date_time = None
    # Check if date_time is a valid date/time object
    if isinstance(date_time, datetime):
      date_time_str = date_time.strftime('%Y-%m-%d %H:%M:%S')
    else:
      date_time_str = "N/A"

    candles.append((date_time_str, open_price, high_price, low_price,
                    close_price, percent_change, up_down))
    previous_close = close_price

  # print(candles)
  candles=candles[::-1]
  return render_template('index.html', candles=candles)


###########################################

def ohlc_to_heiken_ashi(ohlc_array):
  # Initialize the Heiken Ashi array with the same shape as the OHLC array
  heiken_ashi_array = (ohlc_array)

 
  # Set the open price for the first candle in the Heiken Ashi array
 

  # Set the timestamp, open, high, low, and close prices, and volume data for each subsequent candle in the Heiken Ashi array
  for i in range(1, len(ohlc_array)):
   
    heiken_ashi_array[0][1] = (ohlc_array[i-1][1] + ohlc_array[i-1][4]) / 2
    
    heiken_ashi_array[i][4] = (ohlc_array[i][1] + ohlc_array[i][2] + 
    ohlc_array[i][3] + 
    ohlc_array[i][4]) / 4
   

  # Return the Heiken Ashi array
  return heiken_ashi_array




  

def detect_trend_change(ohlc_array):
  # Initialize the trend variable with the value of the first candle's close price
  trend = ohlc_array[0][4]

  # Get the time zone for AEST
  timezone = pytz.timezone("Australia/Sydney")

  # Iterate over the candles in the OHLC array
  for i in range(1, len(ohlc_array)):
    # Check if the current candle's close price is higher than the previous candle's close price
    if ohlc_array[i][4] > ohlc_array[i-1][4]:
      # If the current candle's close price is higher than the previous candle's close price,
      # check if the current trend is a downtrend
      if trend < 0:
        # If the current trend is a downtrend, print a message indicating that the trend has changed
        timestamp = ohlc_array[i][0]
        time = datetime.fromtimestamp(timestamp/1000, 
       tz=timezone)
        print(f"Trend changed at {time} to an uptrend")
      # Set the trend to an uptrend
      trend = 1
    # If the current candle's close price is lower than the previous candle's close price,
    # check if the current trend is an uptrend
    elif ohlc_array[i][4] < ohlc_array[i-1][4]:
      if trend > 0:
        # If the current trend is an uptrend, print a message indicating that the trend has changed
        timestamp = ohlc_array[i][0]
        time = datetime.fromtimestamp(timestamp/1000, tz=timezone)
        print(f"Trend changed at {time} to a downtrend")
      # Set the trend to a downtrend
      trend = -1
    # Check if the current candle is the last candle in the array
    if i == len(ohlc_array) - 1:
      # If the current candle is the last candle in the array, check if the current trend is a downtrend
      if trend < 0:
        # If the current trend is a downtrend, send an IFTTT alert indicating that the trend has changed
        send_ifttt_alert("IFTTT Trend changed to an uptrend")
      # If the current trend is an uptrend, send an IFTTT alert indicating that the trend has changed
      elif trend > 0:
        send_ifttt_alert("IFTT Trend changed to a downtrend")
  


def send_ifttt_alert(message):
  # Set the IFTTT webhook URL
  ifttt_webhook_url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

  # Set the event name and your IFTTT key
  event_name = "trend_change"
  ifttt_key = "your_ifttt_key"

  # Format the webhook URL with the event name and IFTTT key
  url = ifttt_webhook_url.format(event=event_name, key=ifttt_key)

  # Set the payload for the IFTTT alert
  payload = {"value1": message}

  # Send the IFTTT alert
  requests.post(url, json=payload)
######################################
app.run(host='0.0.0.0', port=81)
########################################
