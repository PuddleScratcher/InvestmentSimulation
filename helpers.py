# -------------------------------------------------------------------------
# https://stackoverflow.com/questions/51832672/pandas-excel-days360-equivalent
# Excel-equivalent calculation of days between two dates, based on 360 day calendar

def Days360(start_date, end_date, method_eu=False):
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year
    end_day = end_date.day
    end_month = end_date.month
    end_year = end_date.year

    if (
        start_day == 31 or
        (
            method_eu is False and
            start_month == 2 and (
                start_day == 29 or (
                    start_day == 28 and
                    start_date.is_leap_year is False
                )
            )
        )
    ):
        start_day = 30

    if end_day == 31:
        if method_eu is False and start_day != 30:
            end_day = 1

            if end_month == 12:
                end_year += 1
                end_month = 1
            else:
                end_month += 1
        else:
            end_day = 30

    return (
        end_day + end_month * 30 + end_year * 360 -
        start_day - start_month * 30 - start_year * 360)


# -------------------------------------------------------------------------

"""Investment account that models an amount of cash and a number of shares for
one asset. Provides functionality for gaining interest on the cash and dividend
on the shares.
"""
class Account():
    def __init__(self, cash, interest_rate, annual_dividend, tax_rate = .25 * 1.055):
        self.cash = cash
        self.tax_rate = tax_rate
        self.annual_dividend = annual_dividend * (1-tax_rate)
        self.interest_rate = interest_rate
        self.num_shares = 0
        self.total_investment = 0
        self.SetBuyCost(0, 0)
        
    def SetBuyCost(self, percentage, fee):
        self.buy_percentage = percentage
        self.buy_fee = fee
        
    def Deposit(self, amount):
        self.cash += amount
        
    def BuyShares(self, investment, price, has_fee = True):
        self.num_shares += investment / price
        total_cost = investment + self.BuyCost(investment)
        self.total_investment += investment
        self.cash -= total_cost
    
    def BuyCost(self, investment):
        return investment * self.buy_percentage + self.buy_fee

    def GetStockValue(self, price):
        current_stock = self.num_shares * price
        tax = (current_stock - self.total_investment) * self.tax_rate
        current_stock -= tax
        return current_stock
    
    def GainInterest(self, start_date, end_date):
        days = (end_date-start_date).days
        days = Days360(start_date, end_date)
        self.cash *= (1 + self.interest_rate)**(days/360)
        
    def GainDividend(self, price):
        current_stock = self.GetStockValue(price)
        current_dividend = current_stock * self.annual_dividend/12
        self.cash += current_dividend

# -------------------------------------------------------------------------

class Calendar():
    def __init__(self, start_date):
        self.days_left = 7
        self.start_date = start_date
        
    def Update(self, current_date):
        self.days_left -= 1
        if self.days_left == 0:
            self.days_left = 21

    def IsEndOfMonth(self):
        return self.days_left == 21
    
    def GetDays(self, start_date, current_date):
        return Days360(start_date, current_date)
