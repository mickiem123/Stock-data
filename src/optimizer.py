import pandas as pd

import datetime
import numpy as np
from collections import defaultdict
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from src.helper import Helper

class Optimizer:
    def __init__(self,stocks:list,start_year_previous = 5):
        self.stocks = stocks
        #history is stored as {"symbol":{"close: []"
        #                                 "open":[]
        #                                 "time":[]}}
        #                      
        self.history = defaultdict(dict)
        #calculate date
        today = datetime.date.today()  
        start = str(today.replace(year=today.year - start_year_previous))
        end = str(today.replace(day=today.day - 1))
        # insert data into dictionary
        for i, stock in enumerate(self.stocks):
            data = Helper.historical_data(stock= stock, start_date= start,end_date= end, engine= "vnstock"
                                          ,include = ["close"])
            self.history[stock] = data["close"]
        
        
        # calculate covariance right away here
        self.hpr_df = pd.DataFrame(self.history).pct_change().dropna()
        self.annualized_hpr = self.hpr_df.mean() *252
        self.cov_matrix = self.hpr_df.cov()
    def calculate_variance(self,weight:list):
        weight = np.array(weight)

        return weight @ self.cov_matrix @ weight 
    def calculate_return(self,weight:list):
        weight = np.array(weight)
        return weight@self.annualized_hpr 

    def optimize_portfolio(self, target_return):
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: self.calculate_return(w) - target_return}
        )
        bounds = tuple((0, 1) for _ in range(len(self.stocks)))
        initial_guess = np.array(len(self.stocks) * [1. / len(self.stocks)])
        
        result = minimize(self.calculate_variance, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        if result.success:
            return result.fun**0.5, target_return, result.x  # Return volatility, target return, weights
        else:
            print(f"Optimization failed for target_return={target_return}. Message: {result.message}")
            return None
    def find_MVP(self):

        one_matrix = np.ones((self.cov_matrix.shape[0],1))
        w = np.linalg.inv(self.cov_matrix) @ one_matrix
        self.mvp_w = Helper.normalize_to_1(w)
        return self.mvp_w
    def find_OP(self,risk_free_rate = 0.04):

        excess_return = self.annualized_hpr - risk_free_rate
        w = np.linalg.inv(self.cov_matrix) @ excess_return.T
        self.op_w = Helper.normalize_to_1(w)
        return self.op_w
    
    def efficient_frontier(self,draw=True):
        min_return = self.annualized_hpr.min()
        max_return = self.annualized_hpr.max()
        if pd.isna(min_return) or pd.isna(max_return):
            print("Invalid return range. Check data.")
        else:
            target_returns = np.linspace(min_return, max_return, 50)
            frontier = []
            for tr in target_returns:
                res = self.optimize_portfolio(tr)
                if res:
                    frontier.append(res)

            if draw:
                volatilities, returns, _ = zip(*frontier)
                plt.figure(figsize=(10, 6))
                plt.plot(volatilities, returns, 'b-', label='Effgiticient Frontier')
                plt.scatter(volatilities, returns, c='blue', s=20)
                plt.xlabel('Volatility (Standard Deviation)')
                plt.ylabel('Expected Return')
                plt.title('Efficient Frontier for Portfolio')
                plt.grid(True)
                plt.legend()
                plt.show()
            else:
                print("No valid points on the efficient frontier. Check data or target returns.")


if __name__ == "__main__":
    op = Optimizer(stocks=["ACB","VCB"])
    print(op.hpr_df)
    #print(op.annualized_hpr)
    #print(op.cov_matrix)
    print(op.find_OP())
    print(op.efficient_frontier())