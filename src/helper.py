import pandas as pd
import numpy as np
from collections import defaultdict
from vnstock import Vnstock

class Helper:

    @staticmethod
    def normalize_to_1(mat:np.array):
        total = np.sum(mat)
        return mat / total
    @staticmethod
    def find_risk_free_rate():
        pass
    @staticmethod
    def historical_data(stock:str,
                        start_date:str,
                        end_date:str,
                        engine:str,
                        include = ["time","open","close"]):
        history = defaultdict()
        #perform search by vnstock library
        if engine == "vnstock":
            stock_obj = Vnstock().stock(symbol=stock, source="VCI")
            stock_data = stock_obj.quote.history(start=start_date, end=end_date, interval="1D")
            if stock_data.empty:
                print(f"No data for {stock}")
            else:
                for key in include:
                    if key in stock_data.columns:
                        history[key] = stock_data[key].copy()
        #return a dictionary history {"time", "open","close": 
        # each with a row of data assigned }
        return history
    @staticmethod
    def calculate_variance(hpr_df:pd.DataFrame,weight:list):
        hpr_df.pct_change()