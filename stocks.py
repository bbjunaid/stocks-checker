#!/usr/bin/env python

import datetime
import json

from googlefinance import getQuotes
from pyexcel_xls import get_data
import redis

from auth import GMAIL_USER, GMAIL_PASS, GMAIL_SEND_LIST
from const import ENGAGEMENT_FILE_PATH, CACHE_KEY_TWITTER_STATUS, CACHE_EXPIRY_TIME, CACHE_KEY_TREND, CACHE_TWITTER_STATUS_RETRY
from smtpexample import mail
from twitter_api import get_status_for_first_tweet_of_day, get_statuses_since_id

r = redis.StrictRedis(host='localhost', port=6379, db=0)


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance (obj, datetime.datetime):
            return obj.strftime ('%Y/%m/%d/%H/%M/%S')
        elif isinstance (obj, datetime.date):
            return obj.strftime ('%Y/%m/%d')

        return json.JSONEncoder.default(self, obj)


class Stock(object):
    def __init__(self, symbol, stock_type, suggested_date, trigger_price, current_price, stop_price, options):
        self.symbol = symbol
        self.stock_type = stock_type
        self.suggested_date = suggested_date
        self.trigger_price = trigger_price
        self.current_price = current_price
        self.stop_price = stop_price
        self.options = options

    def is_triggered(self):
        return self.current_price >= self.trigger_price

    def print_stock(self):
        print("{symbol}\t{trigger_price}\t{current_price}".format(symbol=self.symbol,
                                                                  trigger_price=self.trigger_price,
                                                                  current_price=self.current_price))


def is_valid_stock_info(row):
    return row[2] in ['LONG']


def get_suggested_date(row):
    raw_date = row[5].split('/')
    year, month, day = int(raw_date[0]), int(raw_date[1]), int(raw_date[2])
    return datetime.date(year, month, day)


def is_stock_recently_suggested(date_suggested, days_to_consider):
    return date_suggested >= (datetime.date.today() - datetime.timedelta(days=days_to_consider))


def get_recent_stocks_data(data_rows, days_to_consider):
    symbols_list = []
    return_data = {}
    real_data = data_rows[5:]

    for row in real_data:
        if is_valid_stock_info(row):
            date_suggested = get_suggested_date(row)
            if is_stock_recently_suggested(date_suggested, days_to_consider):
                symbol = row[1]
                stock_type = row[2]
                trigger = row[3]
                stop = row[4]
                options = row[6]
                symbols_list.append(symbol)
                return_data[symbol] = {
                    'stock_type': stock_type,
                    'trigger_price': trigger,
                    'stop_price': stop,
                    'suggested_date': date_suggested,
                    'options': options
                }

    return symbols_list, return_data


def create_stock_objects(symbols, recent_stocks):
    stock_objects = []
    stocks_not_found = []
    quotes = getQuotes(symbols)

    for quote in quotes:
        symbol = quote['StockSymbol']
        current_price = quote['LastTradeWithCurrency']
        stock_type = recent_stocks[symbol]['stock_type']
        suggested_date = recent_stocks[symbol]['suggested_date']
        trigger_price = recent_stocks[symbol]['trigger_price']
        stop_price = recent_stocks[symbol]['stop_price']
        options = recent_stocks[symbol]['options']
        try:
            stock_object = Stock(symbol, stock_type, suggested_date, float(trigger_price), float(current_price), float(stop_price), options)
            stock_objects.append(stock_object)
        except:
            stock_object = Stock(symbol, stock_type, suggested_date, float(trigger_price), float(0), float(stop_price), options)
            stocks_not_found.append(stock_object)
            pass

    return stock_objects, stocks_not_found


def send_email_for_triggered_stocks(stocks, stocks_not_found, tweets_symbols_list):
    current_price_style = "background-color: black; color: white;"

    def _generate_table_header(header_label):
        return "<br>{header_label}<br>\
                    <table>\
                    <tr>\
                    <th>Symbol</th>\
                    <th>Long/Short</th>\
                    <th>Trigger Price</th>\
                    <th><b>Current Price</b></th>\
                    <th>Stop Price</th>\
                    <th>Date Suggested</th>\
                    <th>Options</th>\
                    </tr>".format(header_label=header_label, current_price_style=current_price_style)

    def _generate_stock_row(stock):
        return "<tr>\
                    <th>{symbol}</th>\
                    <th>{stock_type}</th>\
                    <th>{trigger_price}</th>\
                    <th><b>{current_price}</b></th>\
                    <th>{stop_price}</th>\
                    <th>{suggested_date}</th>\
                    <th>{options}</th>\
                    </tr>".format(symbol=stock.symbol,
                                  stock_type=stock.stock_type,
                                  trigger_price=stock.trigger_price,
                                  current_price=stock.current_price,
                                  stop_price=stock.stop_price,
                                  suggested_date=stock.suggested_date.strftime('%m/%d/%Y'),
                                  options=stock.options,
                                  current_price_style=current_price_style)

    def _generate_table_with_header_and_data(header_label, core):
        table = _generate_table_header(header_label)
        table += core
        table += "</table>"
        return table

    body = "\
            <html>\
            <head>\
            <style>\
            table {\
                width:100%;\
            }\
            table, th, td {\
                border: 1px solid black;\
            border-collapse: collapse;\
            }\
            th, td {\
                padding: 5px;\
            text-align: left;\
            }\
            table#t01 tr:nth-child(even) {\
            background-color: #eee;\
            }\
            table#t01 tr:nth-child(odd) {\
            background-color:#fff;\
            }\
            table#t01 th {\
            background-color: black;\
            color: white;\
            }\
            </style>\
            </head>\
            <body>"

    triggered_stock_symbols = []
    print "Newly triggered stocks:"
    triggered_core = ""
    previously_triggered_core = ""
    for stock in stocks:
        # only consider stocks we haven't already sent an email about
        if stock.is_triggered():
            triggered_stock_symbols.append(stock.symbol)
            if r.get(stock.symbol):
                previously_triggered_core += _generate_stock_row(stock)
            else:
                r.set(stock.symbol, stock.symbol, ex=CACHE_EXPIRY_TIME)  # expire stock symbol after 7h
                stock.print_stock()
                triggered_core += _generate_stock_row(stock)

    print "Not found stocks:"
    not_found_core = ""
    if stocks_not_found:
        for stock in stocks_not_found:
            # only consider stocks we haven't already sent an email about
            if not r.get(stock.symbol):
                r.set(stock.symbol, stock.symbol, ex=CACHE_EXPIRY_TIME)  # expire stock symbol after 7h
                stock.print_stock()
                not_found_core += _generate_stock_row(stock)

    print "Relevant Tweets"
    tweet_body = ""
    reference_status_id = r.get(CACHE_KEY_TWITTER_STATUS)
    statuses_to_check = get_statuses_since_id(reference_status_id) if reference_status_id else []

    for status in statuses_to_check:
        for symbol in tweets_symbols_list:
            if 'TQQQ' not in status.text and symbol in status.text:
                print status.text
                tweet_body += (status.created_at + ": <b>" + status.text + "</b><br>")

    if len(statuses_to_check) > 0:
        r.set(CACHE_KEY_TWITTER_STATUS, statuses_to_check[0].id, CACHE_EXPIRY_TIME)

    if triggered_core:
        body += _generate_table_with_header_and_data("Newly Triggered Stocks", triggered_core)

    # report previously triggered stocks if we have new triggers / tweets
    if previously_triggered_core and (triggered_core or tweet_body):
        body += _generate_table_with_header_and_data("Previously Triggered Stocks", previously_triggered_core)

    if not_found_core:
        body += _generate_table_with_header_and_data("Could not find current price for these stocks", not_found_core)

    if tweet_body:
        body += "<br>Relevant tweets for triggered stocks<br>"
        body += tweet_body

    body += "</body></html>"

    if triggered_core or not_found_core or tweet_body:
        trend = r.get(CACHE_KEY_TREND)
        subject = "ENGAGED STOCKS"
        if trend:
            subject = trend + ": " + "ENGAGED STOCKS"
        mail(gmail_user=GMAIL_USER,
             gmail_pwd=GMAIL_PASS,
             from_gmail_user="Stocks Software <{email}>".format(email=GMAIL_USER),
             to='',
             subject=subject,
             text='',
             bcc=GMAIL_SEND_LIST,
             html=body)


def main():
    data = get_data(ENGAGEMENT_FILE_PATH)
    json_data = json.loads(json.dumps(data, cls=MyEncoder))
    symbols_list, recent_stocks_data = get_recent_stocks_data(json_data['Sheet1'], days_to_consider=7)
    tweets_symbols_list, _ = get_recent_stocks_data(json_data['Sheet1'], days_to_consider=30)
    stock_objects, stocks_not_found = create_stock_objects(symbols_list, recent_stocks_data)
    status_retry = r.get(CACHE_TWITTER_STATUS_RETRY)
    if not status_retry:
        status_retry = 0

    if not r.get(CACHE_TWITTER_STATUS_RETRY) and status_retry <= 5:
	r.set(CACHE_TWITTER_STATUS_RETRY, status_retry+1)
        reference_status_id = get_status_for_first_tweet_of_day().id
        r.set(CACHE_KEY_TWITTER_STATUS, reference_status_id, ex=CACHE_EXPIRY_TIME)

    send_email_for_triggered_stocks(stock_objects, stocks_not_found, tweets_symbols_list)


if __name__ == "__main__":
    main()
