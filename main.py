
from portfolio import Portfolio
from backends.apis.twelve_data import MyTwelveDataAPI
from backends.apis.alpha_vantage import MyAlphaVantageAPI
from backends.apis.tiingo import MyFinnhubAPI


def main():
    # TODO: need way to see what currency a ticker will return
    global CONFIG
    with open('config.yaml') as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)
    
    backend = build_api()
    # create portfolio class instance with api backend and the defult currency
    p = Portfolio(backend, CONFIG['dataConversions']['defaultCurrency'])
    # load data in & display quickstats
    p.from_csv(CONFIG['data']['filepath'])
    p.quickstats()
    


if __name__ == "__main__":
    main()
