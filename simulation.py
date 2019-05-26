from helpers import Calendar

'''Investment simulation. Iterates over a certain time interval and buys shares
according to the provided strategy (algorithm)
'''
class Simulation():
    def __init__(self, account, algorithm, income, income_raise, verbose = False):
        self.verbose = verbose
        self.account = account
        self.algorithm = algorithm
        self.income = income
        self.income_raise = income_raise
    
    def Initialize(self, data, stock_rate, start, end):
        self.data = data
        
        start = max(start, 1)
        end = min(end, len(data))
        
        self.start_index = start
        self.end_index = end
        
        self.start_date = data.iloc[self.start_index].Datum
        # hack to set startdate to the first of the month
        self.start_date = self.start_date.replace(day=1)

        current_close = data.iloc[self.start_index - 1].Close
        self.account.BuyShares(stock_rate * self.account.cash, current_close, False)
    
    def ProcessDay(self, i, data, prev_data):
        low_price = data['Low']
        open_price = data['Open']
        current_date = data['Datum']
        prev_price = prev_data['Close']
        prev_date = prev_data['Datum']

        current_stock = self.account.GetStockValue(prev_price)
        current_total = self.account.cash + current_stock

        # maybe set new limits for this day
        self.algorithm.Iterate(current_date, prev_price, current_total, current_stock)
       
        # buy stocks
        investment, buy_price = self.algorithm.TryBuy(open_price, low_price, current_total)
        if investment > 0:
            self.account.BuyShares(investment, buy_price)
       
        # gain interest
        self.account.GainInterest(prev_date, current_date)
        
        return current_stock

    def Run(self, algorithm):
        data = self.data

        calendar = Calendar(self.start_date)
        for i in range(self.start_index, self.end_index):
            current_date = data.iloc[i]['Datum']
       
            calendar.Update(current_date)

            self.ProcessDay(i, data.iloc[i], data.iloc[i-1])

            if calendar.IsEndOfMonth():
                days = calendar.GetDays(self.start_date, current_date)
                # add income
                current_income = self.income * (1 + self.income_raise) ** (days / 360)
                algorithm.SetIncome(current_income)
                self.account.Deposit(current_income)
                
                # dividend
                prev_close = data.iloc[i-1]['Close']
                self.account.GainDividend(prev_close)

        
            current_close = data.iloc[i]['Close']
            
            if self.verbose:
                print ("%s |   %.2f   %.2f   %.2f" % (current_date, self.account.num_shares, self.account.GetStockValue(current_close), self.account.cash))

        
        current_stock_value = self.account.GetStockValue(current_close)
        total = current_stock_value + self.account.cash
        
        if self.verbose:
            print("TOTAL: %.0f (%.1f stocks, %.0f cash)" % (total, self.account.num_shares, self.account.cash))

        return total
               
