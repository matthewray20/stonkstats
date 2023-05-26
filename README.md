# Stonk Stats
## Overview
<p> This is a simple program to take data about stock transactions and generate statistics and graphs.</p>

## Functionality
* The 'assetType' field currently works with 'crypto' or 'security'. 
* The 'eventType' field currently works with 'buy', 'sell', or 'split'
* The stats generated for each asset held are: total quentity held, average price, total invested, current value and the multiple of your invested total.
* Stock splits are automatically put at the end of their listed 'date' since they will actualise after market close.
* Create new assets by using Portfolio.add_new_asset
* Add events by using Portfolio.add_asset_event
* Merge assets or portfolios with the option to allow duplicates or not


## How to run
1. Create a new Portfolio class instance
1. Set up manually by using the Portfolio methods set_data_date_format, set_backend, and set_default_currency or set up automatically through a config file.
1. Add data from csv by using add_from_csv or from an existing Portfolio saved as a pickle by using add_from_pickle.
1. Call Portfolio.quickstats() to view the stats in a pretty table

## Notes
<p>This was my first go at taking a simple project of mine and building it out with multiple backend support, error handling and greater robustness.</p>
<p>I know the error handling in the APIs is not the best but it was my first time playing with decorators and I wanted to se them somewhere.

### TODO
* Add GUI
* Add tax report generation