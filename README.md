# fitzstock-checker
Scripts to monitor and alert about stocks recommended by fitzstockcharts

This script will download the daily engagement.xls spreadsheet sent by fitzstockcharts from gmail, parse it, and then find which stocks recommended by fitz in the last week have crossed their trigger price.

It also monitors fitzstockcharts twitter (https://twitter.com/fitzstockcharts) and checks for any tweets regarding the stocks that have triggered.

For any new stocks that trigger or any tweets which contains a triggered stock symbol, this script sends out an email to alert the user to take action on this stock.

Here is an example email that shows stocks that were triggered as well as relevant tweets, all in a single email:

<p align="center">
  <img src="https://postimg.org/image/5bks3pa31/" width="350"/>
  <img src="https://postimg.org/image/pk85pf9e5/" width="350"/>
</p>

![alt tag](https://postimg.org/image/5bks3pa31/)

![alt tag](https://postimg.org/image/pk85pf9e5/)
