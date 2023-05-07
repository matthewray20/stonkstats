
from portfolio import Portfolio

def main():
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    backend = build_api()
    # create portfolio class instance with api backend and the defult currency
    p = Portfolio(backend, config['dataConversions']['defaultCurrency'])
    # load data in & display quickstats
    p.from_csv(config['data']['filepath'])
    p.quickstats()
    


if __name__ == "__main__":
    main()
