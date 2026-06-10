from src.gui import TradingApp

if __name__=='__main__':
    symbols=["GOOG","AAPL","MSFT","TSLA","AMZN","NFLX","META","NVDA","PEP","JPM"]
    app=TradingApp(symbols)
    app.mainloop()