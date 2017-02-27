class TablePrinter:
    def body(self):
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
        return body

    def generate_table_header(self, header_label):
        return "<br>{header_label}<br>\
                    <table>\
                    <tr>\
                    <th>Symbol</th>\
                    <th>Trigger Price</th>\
                    <th><b>Current Price</b></th>\
                    <th>Trigger Change</th> \
                    <th>Daily Change</th> \
                    <th>Volume Ratio</th>\
                    <th>Volume</th> \
                    <th>Avg Daily Volume</th>\
                    </tr>".format(header_label=header_label)

    def generate_stock_row(self, stock):
        return "<tr>\
                    <th>{symbol}</th>\
                    <th>{trigger_price}</th>\
                    <th><b>{current_price}</b></th> \
                    <th style='color: green'>+{percent_change_from_trigger}%</th> \
                    <th style='color: {color}'>{percent_change}</th> \
                    <th>{volume_ratio}</th> \
                    <th>{volume}</th> \
                    <th>{avg_daily_volume}</th>\
                    </tr>".format(symbol=stock.symbol,
                                  trigger_price=stock.trigger_price,
                                  current_price=stock.current_price,
                                  percent_change=stock.percent_change,
                                  percent_change_from_trigger=round(100*(float(stock.current_price)-float(stock.trigger_price))/float(stock.trigger_price), 2),
                                  color='red' if float(stock.percent_change[:-1]) < 0 else 'green',
                                  volume_ratio=round(float(stock.volume)/float(stock.avg_daily_volume), 2),
                                  volume=format(int(stock.volume), ","),
                                  avg_daily_volume=format(int(stock.avg_daily_volume), ","))

    def generate_table_with_header_and_data(self, header_label, core):
        table = self.generate_table_header(header_label)
        table += core
        table += "</table>"
        return table
