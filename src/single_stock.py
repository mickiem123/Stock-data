import pandas as pd
from vnstock import Vnstock
import datetime
import numpy as np
from collections import defaultdict
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from src.helper import Helper


class Stock:
    def __init__(self,stock:"str"):
        self.stock = stock
        #calculate date
        today = datetime.date.today()
        start = str(today.replace(year=today.year - 5))
        end = str(today.replace(day=today.day - 1))
        #initialize history and use helper func to get data
        
        self.history=Helper.historical_data(stock= stock,
                                            start_date= start,
                                            end_date= end,
                                            engine="vnstock")
        #single stock so we can turn data into table immediately
        # no accessing problem
        self.history = pd.DataFrame(self.history)
        #shift close column by 1 
        # and remove the first row ( because empty value)
        # to calculate hpr easily
        
        
        self.history["close_shift_1"] = self.history["close"].shift(1)
        self.history = self.history.iloc[1:,:]
        
    def calculate_hpr(self,display_option = False):
        #calculate hpr day
        self.history["hpr"] = (self.history["close"]- self.history["close_shift_1"]) / self.history["close_shift_1"]
        if display_option:
            print(self.history)
            
    def calculate_arithmethic_mean(self,display_option = False):
        """Calculate arithmethic_mean """ 
        if "hpr" not in self.history.columns:
            self.calculate_hpr()
            
        self.arithmethic_mean = self.history["hpr"].mean()
        if display_option:
            print(f"Arithmethic mean: {self.arithmethic_mean}")
        return self.arithmethic_mean
    
    def calculate_geometric_mean(self,display_option = False):
        """Calulate geometric mean"""
        
        if "hpr" not in self.history.columns:
            self.calculate_hpr()
        
        growth_factors = 1 + self.history["hpr"]
        self.geo_mean = np.prod(growth_factors) ** (1 / len(growth_factors)) - 1
        if display_option:
            print(f"Geometric mean:{self.geo_mean}")
        return self.geo_mean
    
    def calculate_standard_deviation(self,display_option = False):
        """Calculate standard deviation"""
        if "hpr" not in self.history.columns:
            self.calculate_hpr()
        self.std_dev = self.history["hpr"].std()
        if display_option:
            print(f"Standard deviation: {self.std_dev}")  
        return self.std_dev
    
    def annualize_metrics(self,display_option = False):
        trading_days = 252  # typical number of trading days in a year

        # Calculate missing values if needed
        if not hasattr(self, 'arithmethic_mean'):
            self.calculate_arithmethic_mean()
        if not hasattr(self, 'geo_mean'):
            self.calculate_geometric_mean()
        if not hasattr(self, 'std_dev'):
            self.calculate_standard_deviation()

        self.annualized_mean = (1 + self.geo_mean) ** trading_days - 1
        self.annualized_std = self.std_dev * np.sqrt(trading_days)
        self.annualized_amean = self.arithmethic_mean * trading_days

        result= {
            "Annualized_arithmethic_mean": self.annualized_amean,
            "Annualized_geometric_mean": self.annualized_mean,
            "Annualized_std": self.annualized_std,
        }
        
        if display_option:
            print(pd.DataFrame(result))
            
        return result
    
    def display_results(self):
        results = {
            "Arithmethic mean": [],
            "Geometric mean": [],
            "Standard deviation": []
        }

        # Calculate non-annualized metrics only if missing
        if not hasattr(self, 'arithmethic_mean'):
            self.calculate_arithmethic_mean()
        if not hasattr(self, 'geo_mean'):
            self.calculate_geometric_mean()
        if not hasattr(self, 'std_dev'):
            self.calculate_standard_deviation()

        # Calculate annualized metrics only if missing
        if not hasattr(self, 'annualized_amean') or not hasattr(self, 'annualized_mean') or not hasattr(self, 'annualized_std'):
            self.annualize_metrics()

        results["Arithmethic mean"].append(self.arithmethic_mean)
        results["Geometric mean"].append(self.geo_mean)
        results["Standard deviation"].append(self.std_dev)

        results["Arithmethic mean"].append(self.annualized_amean)
        results["Geometric mean"].append(self.annualized_mean)
        results["Standard deviation"].append(self.annualized_std)

        df = pd.DataFrame(results, index=["Not annualized", "Annualized"])
        print(df)
        
if __name__ == "__main__":
    stock = Stock(stock = "VCB")
    stock.display_results()