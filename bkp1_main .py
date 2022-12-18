from ccxt import kraken
from datetime import datetime
from flask import Flask, render_template

# Create a Flask app
app = Flask(__name__)

@app.route('/')
def index():
  # Create a Kraken client
  client = kraken()

  # Set the timeframe to 15 minutes
  timeframe = '15m'

  # Get the OHLC data for BTC
  ohlcv = client.fetch_ohlcv('BTC/USD', timeframe=timeframe)

  # Calculate the percentage change and "Up/Down" value for each candle
  candles = []
  previous_close = ohlcv[0][4]
  for candle in ohlcv:
    # Get the open, high, low, and close values from the candle data
    timestamp = candle[0]
    open_price = candle[1]
    high_price = candle[2]
    low_price = candle[3]
    close_price = candle[4]
    volume = candle[5]
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
      
    candles.append((date_time_str, open_price, high_price, low_price, close_price,            percent_change, up_down))
    previous_close = close_price

    return render_template('index.html', candles=candles)




###########################################
app.run(host='0.0.0.0', port=81)
########################################
