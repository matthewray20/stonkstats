# Stonk Stats
## Overview
<p> This is a simple program to take data about stock transactions and generate statistics and graphs.</p>

## Functionality
* The 'assetType' field currently works with 'crypto' or 'security'. 
* The 'eventType' field currently works with 'buy', 'sell', or 'split'
* The stats generated for each asset held are: total quentity held, average price, total invested, current value and the multiple of your invested total.
* Stock splits are automatically put at the end of their listed 'date' since they will actualise after market close.
* New events can be added on top of existing data using the Asset.add_event method


## How to run
1. Once your stock transaction data is in csv format, set the path to the file in the config file
1. Set the data headers in the config file. To work out of the box they should be 'assetType', 'price', 'ticker', 'quantity', 'eventType', 'date', 'currency' and 'commision' in any order.
1. Paste your API key for the specific backend you choose in backends/apis/API_keys.yaml
1. Choose your default currency and set the format of the dates of your data in the config file
1. Run main.py

## Notes
<p>This was my first go at taking a simple project of mine and building it out with multiple backend support, error handling and greater robustness.</p>
<p>I know the error handling in the APIs is not the best but it was my first time playing with decorators and I wanted to se them somewhere.