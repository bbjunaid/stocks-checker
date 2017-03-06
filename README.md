# stocks-checker
Scripts to monitor and alert about stocks recommended by fitzstockcharts/chartpattern.

## Fitzstock

    stocks.py

This script will download the daily engagement.xls spreadsheet sent by fitzstockcharts from gmail, parse it, and then find which stocks recommended by fitz in the last week have crossed their trigger price.

It also monitors fitzstockcharts twitter (https://twitter.com/fitzstockcharts) and checks for any tweets regarding the stocks that have triggered.

For any new stocks that trigger or any tweets which contains a triggered stock symbol, this script sends out an email to alert the user to take action on this stock.

Here is an example email that shows stocks that were triggered as well as relevant tweets, all in a single email:

<p align="center">
  <img src="https://s29.postimg.org/hi5oirkx3/Screen_Shot_2017_01_10_at_11_47_38_AM.png"/>
</p>

To obtain real time stock prices, I use the python client for the Google Finance API. Similarly for twitter, I used a twitter client. I used smtp to send emails, and the Gmail python client for reading the excel spreadsheet from the gmail inbox.

An example engagement.xls spreadsheet is attached in the repository to get an example of how the format is.

I use crontabs to run these scripts. The first crontab happens at 8:58AM EST, where we clear out the redis cache, download the engagement spreadsheet. 

Thereafter, from 9AM-5PM EST, we run the stocks script every 2 minutes to check for new triggers/tweets. Here is an example crontab line:

```
# east coast market hours
58 8 * * 1-5 /Users/bilaljunaid/Dropbox/Full_Time_Jobs/code_practice/stocks/scripts/start_day.sh
*/2 9-16 * * 1-5 /Users/bilaljunaid/Dropbox/Full_Time_Jobs/code_practice/stocks/scripts/stocks.sh
```

## Chartpattern

    stocks_dano.py
    
This script monitors a google spreadsheet maintained by me and my friend based on stocks recommended on chartpattern. It parses the google sheet, monitors the stock prices, and sends email when stocks alert. The columns are slightly different as Dano recommends trading based on volume as well:

<p align="center">
  <img src="https://s2.postimg.org/w5xqs2fzt/Screen_Shot_2017_03_05_at_9_46_13_PM.png"/>
</p>
