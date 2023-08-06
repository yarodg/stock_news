import requests
from twilio.rest import Client

# Constants.
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Alpha Vantage API.
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
# Your API key for alpha vantage.
API_STOCK_KEY = ""

# News API
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
# Your API key for news.
API_NEWS_KEY = ""

# Twilio
TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""
# Your Twilio number.
TWILIO_NUM = ""
# Your phone number.
MY_PHONE_NUM = ""

# Getting closing stock price.
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": API_STOCK_KEY
}
response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]

# Getting the yesterday closing price data.
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]

# Getting the day before yesterday closing price data.
day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

# Calculating the % difference.
difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)

up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

diff_percent = round((difference / float(yesterday_closing_price)) * 100)

# # Other way of doing this.
# mean_value = (float(yesterday_closing_price) + float(day_before_yesterday_closing_price)) / 2
# diff_percent = (difference / mean_value) * 100

# If percentage changed significantly -> search for the latest news about the company.
if abs(diff_percent) >= 5:
    news_params = {
        "apiKey": API_NEWS_KEY,
        "qInTitle": COMPANY_NAME,
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]

    # Slicing the articles.
    three_articles = articles[:3]

    # Prepare new list with description for sms sending.
    formatted_articles = [f"{STOCK_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]

    # Sending each articles as separate message via twilio.
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=TWILIO_NUM,
            to=MY_PHONE_NUM
        )

