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
                    <th>Daily Change</th>\
                    <th>Vol Ratio</th>\
                    <th>Vol</th>\
                    <th>Avg Vol</th>\
                    <th>Earnings</th>\
                    </tr>".format(header_label=header_label)

    def generate_stock_row(self, stock):
        return "<tr>\
                    <th>{symbol}</th>\
                    <th>{trigger_price}</th>\
                    <th><b>{current_price}</b></th> \
                    <th style='color: {color_trigger}'>{percent_change_from_trigger}</th> \
                    <th style='color: {color_change}'>{percent_change}</th> \
                    <th>{vol_ratio}</th>\
                    <th>{vol}</th>\
                    <th>{avg_vol}</th>\
                    <th>{earnings}</th>\
                    </tr>".format(symbol=stock.symbol,
                                  trigger_price=stock.trigger_price,
                                  current_price=stock.current_price,
                                  percent_change=('+' if stock.percent_change >= 0 else '') + str(stock.percent_change) + '%',
                                  color_change='red' if stock.percent_change < 0 else 'green',
                                  percent_change_from_trigger=('+' if stock.percent_change_from_trigger >= 0 else '') + str(stock.percent_change_from_trigger) + '%',
                                  color_trigger='red' if stock.percent_change_from_trigger < 0 else 'green',
                                  vol_ratio=stock.vol_ratio,
                                  vol=stock.vol,
                                  avg_vol=stock.avg_vol,
                                  earnings=stock.earnings)

    def generate_table_with_header_and_data(self, header_label, core):
        table = self.generate_table_header(header_label)
        table += core
        table += "</table>"
        return table
