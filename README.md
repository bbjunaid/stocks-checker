# stocks-checker
Scripts to monitor and alert about stocks recommended by fitzstockcharts/chartpattern.

## Instructions

Setup virtualenv:

    ./scripts/setup.sh
    
Activate virtualenv:

    . virtualenv/bin/activate
    
Fill in credentials:

    auth.py
    
Download redis and deamonize it:

    brew install redis
    /usr/local/bin/redis-server --daemonize yes

Run either script:

    python stocks.py
    python stocks_dano.py

For fitzstock, you need a twitter account that follows fitzstockcharts and generate consumer and access keys from https://dev.twitter.com. You also need to ensure you're receiving the spreadsheet daily from Fitz. You need to fill in your gmail username, password, and desired mailing list.

For chartpattern, you need to generate google drive api keys and save them in a JSON and update the GDRIVE_API_KEY_PATH. Then you need to create a google spreadsheet with the stock symbols as the first column and their trigger prices as second column to receive alerts.
   
## Fitzstock

    stocks.py

This script will download the daily engagement.xls spreadsheet sent by fitzstockcharts from gmail, parse it, and then find which stocks recommended by fitz in the last week have crossed their trigger price.

It also monitors fitzstockcharts twitter (https://twitter.com/fitzstockcharts) and checks for any tweets regarding the stocks that have triggered.

For any new stocks that trigger or any tweets which contains a triggered stock symbol, this script sends out an email to alert the user to take action on this stock.

Here is an example email that shows stocks that were triggered as well as relevant tweets, all in a single email:

![Screenshot](https://cloud.githubusercontent.com/assets/1175122/25125605/486975f6-23e4-11e7-8b5e-68e2ce91bfd2.png)

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

![Screenshot](https://cloud.githubusercontent.com/assets/1175122/25125614/4f90db44-23e4-11e7-8c4a-48c4e735285b.png)
