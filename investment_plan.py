'''
Abstract class of an investment plan, which decides to buy stocks depending
on the current price, total investment, date, and/or other factors
'''
class InvestmentPlan:
    def Iterate(date, price):
        return 0
    
    def OnBuy():
        pass
    
    def SetIncome(self, income):
        pass
    
class BargainHunt(InvestmentPlan):
    def __init__(self, dk_fix, risk_part):
        InvestmentPlan.__init__(self)
        self.dk_fix = dk_fix
        self.risk_part = risk_part
        self.force = True
        self.limit = 0
        
    def GetLimit(self, price, total_value, stock_value, stock_part = 1):
        position = stock_value
        r = self.risk_part
        current_t = -total_value * stock_part * r*(1-r) * self.dk_fix
        current_dK = (((total_value * stock_part - position - current_t) * r/(1-r) - current_t) / position) - 1
        limit = price * (1 + current_dK)
        return limit

    def TryBuy(self, open_price, low_price, current_total, stock_part = 1):
        investment = 0
        
        if low_price < self.limit:
            r = self.risk_part
            investment = -current_total * stock_part * r*(1-r) * self.dk_fix
            self.OnBuy()

        return investment, self.limit
    
    def OnBuy(self):
        self.force = True

class OriginalBargainHunt(BargainHunt):
    def __init__(self, dk_fix, risk_part):
        self.days_left = 7
        BargainHunt.__init__(self, dk_fix, risk_part)
    
    def Iterate(self, date, price, total_value, stock_value):
        self.days_left -= 1
        if self.force or self.days_left == 0:
            self.limit = self.GetLimit(price, total_value, stock_value)
            self.force = False
        if self.days_left == 0:
            self.days_left = 21
        return self.limit

class DayOfMonthBargainHunt(BargainHunt):
    def __init__(self, dk_fix, start_date, day, risk_part):
        self.prev_date = start_date
        BargainHunt.__init__(self, dk_fix, risk_part)

    def Iterate(self, date, price, total_value, stock_value):
        is_new_month = date.day > 10 and self.prev_date.day < 10
        
        if self.force or is_new_month:
            self.limit = self.GetLimit(price, total_value, stock_value)
            self.force = False
            
        self.prev_date = date
        return self.limit

class FrequentBargainHunt(BargainHunt):
    def __init__(self, dk_fix, start_date, risk_part, frequency):
        self.prev_date = start_date
        self.frequency = frequency
        BargainHunt.__init__(self, dk_fix, risk_part)

    def Iterate(self, date, price, total_value, stock_value):
        delta = date - self.prev_date
        if self.force or delta.days >= self.frequency:
            
            self.limit = self.GetLimit(price, total_value, stock_value)
            self.force = False
            self.prev_date = date
        return self.limit

class SavingsPlan(InvestmentPlan):
    def __init__(self, investment, fraction):
        self.days_left = 7
        self.investment = investment
        self.fraction = fraction
        InvestmentPlan.__init__(self)

    def SetIncome(self, income):
        self.investment = income
    
    def TryBuy(self, open_price, low_price, current_total):
        investment = 0
        if self.days_left == 21:
            investment = self.investment * self.fraction

        return investment, open_price

    def Iterate(self, date, price, total_value, stock_value):
        self.days_left -= 1
        if self.days_left == 0:
            self.days_left = 21
        return 0
