import gspread
import redis
from oauth2client.service_account import ServiceAccountCredentials
from yahoo_finance import Share

from auth import GDRIVE_API_KEY_PATH, GMAIL_USER, GMAIL_PASS, GMAIL_SEND_LIST
from const import CACHE_EXPIRY_TIME
from printer import TablePrinter
from smtpexample import mail

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name(GDRIVE_API_KEY_PATH, scope)

gc = gspread.authorize(credentials)

r = redis.StrictRedis(host='localhost', port=6379, db=0)


class Stock:
    def __init__(self, symbol, trigger_price, current_price, percent_change, volume, avg_daily_volume):
        self.symbol = symbol
        self.trigger_price = trigger_price
        self.current_price = current_price
        self.percent_change = percent_change if percent_change else '0%'
        self.volume = volume
        self.avg_daily_volume = avg_daily_volume

    def is_triggered(self):
        return self.current_price >= self.trigger_price

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
        share = Share(symbol)
        stock = Stock(symbol, trigger[idx], share.get_price(), share.get_percent_change(), share.get_volume(), share.get_avg_daily_volume())
        stock.print_stock()
        stocks.append(stock)
    return stocks


def send_email(stocks):
    printer = TablePrinter()
    body = printer.body()
    triggered_core = ""
    prev_core = ""
    is_triggered = False
    is_prev_triggered = False
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

    if is_triggered:
        body += printer.generate_table_with_header_and_data("Triggered Stocks", triggered_core)
    if is_prev_triggered:
        body += printer.generate_table_with_header_and_data("Previously Triggered", prev_core)
    body += "</body></html>"

    if is_triggered:
        subject = "DANO STOCKS"
        mail(gmail_user=GMAIL_USER,
             gmail_pwd=GMAIL_PASS,
             from_gmail_user="Stocks Software <{email}>".format(email=GMAIL_USER),
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
