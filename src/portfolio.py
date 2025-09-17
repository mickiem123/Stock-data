import pandas as pd
import datetime
import numpy as np
from collections import defaultdict
from src.helper import Helper


class Portfolio():
    def __init__(self, stocks: list, weight_list: list, start_year_previous=5,):
        #normalize weight to sum 1
        if len(stocks) != len(weight_list):
            raise ValueError("Length of weight_list must equal length of stockS")
        self.weight_list = Helper.normalize_to_1(np.array(weight_list))
        self.stocks = stocks
        #history is stored as {"symbol":{"close: []"
        #                                 "open":[]
        #                                 "time":[]}}
        #                      
        self.history = defaultdict(list)
        #calculate date
        today = datetime.date.today()  # 02:16 PM +07, Aug 29, 2025
        start = str(today.replace(year=today.year - start_year_previous))
        end = str(today.replace(day=today.day - 1))
        # insert data into dictionary
        for i, stock in enumerate(self.stocks):
            data = Helper.historical_data(stock= stock, start_date= start,end_date= end, engine= "vnstock")
            self.history[stock] = data
            
    def export_history(self):
        """Export data to excel"""
        history_df = self.history
        return history_df

    def calculate_hpr(self, display_option=False):
        #create hpr_df table
        self.hpr_df = pd.DataFrame(columns=["stocks", "annualized_return"])
        #expand the dictionary to df, and calculate pct change ( hpr)
        for stock,data in self.history.items():
            # before dataframe, data is {"time":[n],"close":[n],"open":[n]}
            data = pd.DataFrame(data)
            # dont drop na to save it and drop later
            data["return"] = data["close"].pct_change()
            
            if data["return"].empty:
                print(f"No valid returns for {stock}")
                continue
            self.history[stock]["return"] = data["return"].copy()
        #annualize, drop na because the first date doesnt have a date before it to
        #calculate hpr
            overall_return = data["return"].dropna().mean() * 252  # Annualized return
            self.hpr_df = pd.concat([self.hpr_df, pd.DataFrame({"stocks": [stock], "annualized_return": [overall_return]})], ignore_index=True)
        if display_option:
            print(self.hpr_df)
        return self.hpr_df

    def calculate_portfolio_return(self):

        if self.hpr_df.empty or self.hpr_df.isna().all().any():
            print("Warning: Empty or NaN data in returns")
            return 0.0
        hpr_annualized = np.array(self.hpr_df.loc[:,"annualized_return"])
        self.portfolio_return = np.dot(self.weight_list,hpr_annualized )
        return self.portfolio_return

    def calculate_portfolio_variance(self):
        if self.hpr_df.empty or self.hpr_df.isna().all().any():
            print("Warning: Empty or NaN data in returns")
            return 0.0
        
        self.cov_matrix = pd.DataFrame({symbol: data["return"] for symbol, data in self.history.items()}).dropna().cov()
        # turn the data stored into a stock x return table then calculate cov matrix

        return np.dot(self.weight_list.T, np.dot(self.cov_matrix, self.weight_list))

 
if __name__ == "__main__":
    portfolio = Portfolio(stocks=["ACB","VCB"],weight_list=[4,5])
    print(portfolio.calculate_hpr())
    print(portfolio.calculate_portfolio_return())
    print(portfolio.calculate_portfolio_variance())