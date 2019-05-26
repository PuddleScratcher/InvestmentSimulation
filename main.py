# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 23:37:01 2018

@author: PuddleScratcher
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from investment_plan import SavingsPlan, OriginalBargainHunt, DayOfMonthBargainHunt, FrequentBargainHunt
from simulation import Simulation
from helpers import Account

def LoadData(filename):
    dateparse = lambda x: pd.datetime.strptime(x, '%d.%m.%Y')
    data = pd.read_csv(filename, sep=';', parse_dates=['Datum'], date_parser=dateparse, decimal=",", thousands=".")
    # inverse order of data
    data = data.iloc[::-1]
    return data

# -------------------------------------------------------------------------

def FindMonthStart(data):
    dates = []
    for i in range(1, len(data)):
        if data.iloc[i-1].Datum.month != data.iloc[i].Datum.month:
            dates.append(i)
    return dates

def FindYearStart(data):
    dates = [1]
    for i in range(2, len(data)):
        if data.iloc[i-1].Datum.year != data.iloc[i].Datum.year:
            dates.append(i)
    dates.append(len(data))
    return dates

# -------------------------------------------------------------------------

# runs investment simulation on the provided dataset of stock values from start
# to end date, with the provided annual dividend for stock assets and the rate
# of annual income increase
def Simulate(data, start, end, dividend, income_raise):
    account = Account(cash = 20000, interest_rate = .02, annual_dividend = dividend)
    start_date = data.iloc[start].Datum
    
    # optional: buy costs for stocks
    #account.SetBuyCost(percentage = 0.02, fee = 0)
    
    algorithm = OriginalBargainHunt(dk_fix = -0.05, risk_part = 0.5)
    #algorithm = DayOfMonthBargainHunt(dk_fix = -0.05, start_date = start_date, day = 10, risk_part = 0.5)
    #algorithm = FrequentBargainHunt(dk_fix = -0.05, start_date = start_date, risk_part = 0.5, frequency = 2)
    #algorithm = SavingsPlan(200, 0.5)
    
    simulation = Simulation(account, algorithm = algorithm, income = 200, income_raise = income_raise, verbose = True)
    simulation.Initialize(data, start = start, end = end, stock_rate = 0.5)
    
    return simulation.Run(algorithm)

# -------------------------------------------------------------------------

# Simulate the investment plan over all possible combinations
# of start and end years
def OverAllYears(data):
    year_starts = FindYearStart(data)
    n = len(year_starts)
    results = np.zeros(shape = (n, n))
    
    for start in range(n):
        for end in range(n):
            i_start = year_starts[start]-1
            i_end = year_starts[end]-1
            if start < end:
                r = Simulate(data, i_start, i_end)
                s = data.iloc[i_start].Datum.year
                e = data.iloc[i_end].Datum.year
                
                print("%.0f-%.0f: %.2f" % (s, e, r))
                results[start, end] = r
                
    return results

# -------------------------------------------------------------------------

data = LoadData("sp500.csv")
total = Simulate(data, start = 1, end = len(data), dividend = 0.016, income_raise = 0.024)

#data = LoadData("euro600.csv")
#total = Simulate(data, start = 1, end = len(data), dividend = 0.03, income_raise = 0.024)

#data = LoadData("russel.csv")
#total = Simulate(data, start = 1, end = len(data), dividend = 0.026, income_raise = 0.03)

#data = LoadData("Nikkei225.csv")
#total = Simulate(data, start = 1, end = len(data), dividend = 0.025, income_raise = 0.024)

#results = OverAllYears(data)
#np.savetxt("savingsplan_russel.csv", results, fmt = '%10.5f', delimiter=',')

