import re

from googlefinance import getQuotes
from bs4 import BeautifulSoup
import gspread
import redis
import requests
from oauth2client.service_account import ServiceAccountCredentials

from auth import GDRIVE_API_KEY_PATH, GMAIL_USER, GMAIL_PASS, GMAIL_SEND_LIST
from const import CACHE_EXPIRY_TIME
from printer import TablePrinter
from smtpexample import mail

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name(GDRIVE_API_KEY_PATH, scope)

gc = gspread.authorize(credentials)

r = redis.StrictRedis(host='localhost', port=6379, db=0)


class Stock:
    def __init__(self, symbol, trigger_price, current_price=0, percent_change=0,
                 percent_change_from_trigger=0, vol='N/A', avg_vol='N/A', vol_ratio='N/A', earnings='N/A'):
        self.symbol = symbol
        self.trigger_price = trigger_price
        self.current_price = current_price
        self.percent_change = percent_change
        self.percent_change_from_trigger = percent_change_from_trigger
        self.vol = vol
        self.avg_vol = avg_vol
        self.vol_ratio = vol_ratio
        self.earnings = earnings

    def update(self):
        self.current_price = round(float(getQuotes(self.symbol)[0]['LastTradePrice']), 2)
        self.percent_change = round((float(getQuotes(self.symbol)[0]['LastTradePrice']) /
                                     float(getQuotes(self.symbol)[0]['PreviousClosePrice']) - 1)*100, 2)
        self.percent_change_from_trigger = round((self.current_price - self.trigger_price) /
                                                  self.trigger_price * 100, 2)
        self.update_volume()
        self.update_earnings()

    def is_triggered(self):
        return self.current_price >= self.trigger_price

    def update_volume(self):
        try:
            resp = requests.get('http://finance.yahoo.com/quote/{symbol}'.format(symbol=self.symbol))
            soup = BeautifulSoup(resp.content, 'html.parser')
            self.vol = soup.find('td', attrs={'data-test': 'TD_VOLUME-value'}).text
            self.avg_vol = soup.find('td', attrs={'data-test': 'AVERAGE_VOLUME_3MONTH-value'}).text
            self.vol_ratio = round(float(self.vol.replace(',', ''))/float(self.avg_vol.replace(',', '')), 2)
        except Exception as e:
            print e.message

    def update_earnings(self):
        try:
            resp = requests.get('http://www.nasdaq.com/earnings/report/{symbol}'.format(symbol=self.symbol))
            m = re.search("Earnings announcement\* for \w+: (.*)", resp.content)
            date = m.group(1).strip()
            if m and date:
                self.earnings = date
        except Exception as e:
            print e.message

    def print_stock(self):
        print self.__dict__


def get_stocks():
    wks = gc.open('Stocks Watch - Dano').sheet1
    symbols = wks.col_values(1)
    trigger = wks.col_values(2)
    symbols = filter(lambda s: len(s) > 0, symbols)[1:]
    trigger = filter(lambda s: len(s) > 0, trigger)[1:]
    if len(symbols) != len(trigger):
        print "Stocks and triggers are not equal size!"
        return None
    stocks = []
    for idx, symbol in enumerate(symbols):
        stock = Stock(symbol, float(trigger[idx]))
        try:
            stock.update()
        except Exception as e:
            print e.message
            print "Cannot find full info for {symbol}".format(symbol=stock.symbol)
        stock.print_stock()
        stocks.append(stock)
    return stocks


def send_email(stocks):
    printer = TablePrinter()
    body = printer.body()
    triggered_core = ""
    prev_core = ""
    not_triggered_core = ""
    is_triggered = False
    is_prev_triggered = False
    is_not_triggered = False
    for stock in stocks:
        if stock.is_triggered():
            if r.get(stock.symbol):
                print "Previously Triggered: {symbol}".format(symbol=stock.symbol)
                prev_core += printer.generate_stock_row(stock)
                is_prev_triggered = True
            else:
                print "Triggered: {symbol}".format(symbol=stock.symbol)
                r.set(stock.symbol, stock.symbol, ex=CACHE_EXPIRY_TIME)  # expire stock symbol after 7h
                triggered_core += printer.generate_stock_row(stock)
                is_triggered = True
        else:
            not_triggered_core += printer.generate_stock_row(stock)
            is_not_triggered = True

    if is_triggered:
        body += printer.generate_table_with_header_and_data("Triggered Stocks", triggered_core)
    if is_prev_triggered:
        body += printer.generate_table_with_header_and_data("Previously Triggered", prev_core)
    if is_not_triggered:
        body += printer.generate_table_with_header_and_data("Stocks Below Trigger", not_triggered_core)
    body += "</body></html>"

    if is_triggered:
        subject = "DANO STOCKS"
        mail(gmail_user=GMAIL_USER,
             gmail_pwd=GMAIL_PASS,
             from_gmail_user="Terri Software <{email}>".format(email=GMAIL_USER),
             to='',
             subject=subject,
             text='',
             bcc=GMAIL_SEND_LIST,
             html=body)


def main():
    stocks = get_stocks()
    send_email(stocks)


if __name__ == "__main__":
    main()
