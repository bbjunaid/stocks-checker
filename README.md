# fitzstock-checker
Scripts to monitor and alert about stocks recommended by fitzstockcharts

This script will download the daily engagement.xls spreadsheet sent by fitzstockcharts from gmail, parse it, and then find which stocks recommended by fitz in the last week have crossed their trigger price.

It also monitors fitzstockcharts twitter (https://twitter.com/fitzstockcharts) and checks for any tweets regarding the stocks that have triggered.

For any new stocks that trigger or any tweets which contains a triggered stock symbol, this script sends out an email to alert the user to take action on this stock.

Here is an example email that shows stocks that were triggered as well as relevant tweets, all in a single email:

<p align="center">
  <img src="https://s30.postimg.org/o3wn7a6hd/Screen_Shot_2017_01_09_at_2_25_22_PM.png"/>
  <img src="https://s28.postimg.org/zc1qeyclp/Screen_Shot_2017_01_09_at_2_32_13_PM.png"/>
</p>
