import numpy as np
import pandas as pd
import datetime

class StockSimulator:
    def __init__(self, symbol, start_price=100.0, mu=0.0005, sigma=0.02, days=120):
        self.symbol=symbol
        self.mu=mu
        self.sigma=sigma
        self.days=days
        self.current_day=0

        self.dates=pd.date_range(datetime.date.today(),periods=days,freq='B')
        Z=np.random.randn(days)

        closes=np.zeros(days)
        closes[0]=start_price

        for t in range(1,days):
            #S(t) = S(t-1)*e^((u-1/2*sig^2)+sig*Z(t))
            closes[t]=closes[t-1]*np.exp((mu-0.5*sigma**2)+sigma*Z[t])

        
        opens=np.concatenate([[start_price],closes[:-1]])

        highs=np.maximum(opens,closes)*(1+np.random.rand(days)*0.02)
        lows=np.minimum(opens,closes)*(1-np.random.rand(days)*0.02)

        self.data=pd.DataFrame({'Open':opens,'High':highs,'Low':lows,'Close':closes},index=self.dates)

        # print(self.dates)
        # print(Z)
        # print(opens)
        # print(closes)
        # print(highs)
        # print(lows)
        # print(self.data)

    def advance(self):
        if self.current_day<self.days-1:
            self.current_day+=1

    def view(self):
        return self.data.iloc[:self.current_day+1]
    
    def price(self):
        return float(self.data['Close'].iloc[self.current_day])
    
    
# if __name__=='__main__':
#     test_stock=StockSimulator("AAPL")
#     print(f"Created stock: {test_stock.symbol} starting at day {test_stock.current_day}")
#     print(test_stock.view())