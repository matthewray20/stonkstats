
from portfolio import Portfolio
from portfolio import build_api
import yaml

def main():
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    backend = build_api(config)
    # create portfolio class instance with api backend and the defult currency
    p = Portfolio(backend, config['dataConversions']['defaultCurrency'])
    # load data in & display quickstats
    p.add_from_csv(config)
    p.quickstats()
    


if __name__ == "__main__":
    main()
