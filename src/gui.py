import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import mplfinance as mpf
from src.simulation import StockSimulator

class TradingApp(tk.Tk):
    def __init__(self,symbols):
        super().__init__()

        self.title("Multi-Stock Trading Simulator")
        self.geometry("1400x900")

        #State
        self.stocks={s:StockSimulator(s,start_price=50+100*np.random.rand()) for s in symbols}
        self.portfolio={s:0 for s in symbols}
        self.selected=symbols[0]
        self.initial_cash=10000.0
        self.cash=self.initial_cash
        self.commission_fee=1

        #Fonts & Styles
        self.font_label=("Segoe UI",14)
        self.font_btn=("Segoe UI",12,"bold")

        #Layout Frame
        self.frm_chart=ttk.Frame(self)
        self.frm_chart.pack(fill=tk.BOTH,expand=True,padx=10,pady=5)
        self.frm_ctrl=ttk.Frame(self)
        self.frm_ctrl.pack(fill=tk.X,padx=10,pady=5)
        self.frm_status=ttk.Frame(self)
        self.frm_status.pack(fill=tk.X,side=tk.BOTTOM)
        self.frm_log=ttk.Frame(self.frm_chart)
        self.frm_log.pack(side=tk.RIGHT,fill=tk.Y,padx=(10,0))

        #Matplotlib Canvas
        self.fig,self.ax=plt.subplots(figsize=(10,7))
        self.canvas=FigureCanvasTkAgg(self.fig,master=self.frm_chart)
        self.canvas.get_tk_widget().pack(side=tk.LEFT,fill=tk.BOTH,expand=True)

        #Display
        ttk.Label(self.frm_log,text="Trade Log",font=self.font_btn).pack(anchor=tk.W)
        self.log_box=tk.Listbox(self.frm_log,width=35,font=self.font_label)
        self.log_box.pack(fill=tk.BOTH,expand=True)

        #Controls
        ttk.Label(self.frm_ctrl,text="Stock:",font=self.font_label).pack(side=tk.LEFT)
        self.sym_var=tk.StringVar(value=self.selected)
        ttk.Combobox(self.frm_ctrl,textvariable=self.sym_var,values=symbols,state="readonly",width=10,font=self.font_label).pack(side=tk.LEFT,padx=5)
        tk.Button(self.frm_ctrl,text="Switch",bg="Indigo",fg="white",font=self.font_btn,command=self.on_switch).pack(side=tk.LEFT,padx=(5,20))

        ttk.Label(self.frm_ctrl,text="Price:",font=self.font_label).pack(side=tk.LEFT)
        self.price_var=tk.StringVar(value="0.00")
        ttk.Label(self.frm_ctrl,textvariable=self.price_var,font=self.font_label,width=10).pack(side=tk.LEFT,padx=(5,20))
        
        ttk.Label(self.frm_ctrl,text="Qty:",font=self.font_label).pack(side=tk.LEFT)
        self.qty_var=tk.IntVar(value=0)
        ttk.Entry(self.frm_ctrl,textvariable=self.qty_var,font=self.font_label,width=6).pack(side=tk.LEFT,padx=(5,20))

        tk.Button(self.frm_ctrl,text="Buy",bg="green",fg="white",font=self.font_btn,command=self.buy).pack(side=tk.LEFT,padx=5)
        tk.Button(self.frm_ctrl,text="Sell/Short",bg="red",fg="white",font=self.font_btn,command=self.sell).pack(side=tk.LEFT,padx=5)
        tk.Button(self.frm_ctrl,text="Next Day",bg="orange",fg="white",font=self.font_btn,command=self.on_next).pack(side=tk.LEFT)
        tk.Button(self.frm_ctrl,text="Exit Positions",bg="blue",fg="white",font=self.font_btn,command=self.on_exit_position).pack(side=tk.LEFT,padx=(10,0))
        tk.Button(self.frm_ctrl,text="Exit",bg="grey",fg="white",font=self.font_btn,command=self.exit_app).pack(side=tk.RIGHT)
      
        self.cash_var=tk.StringVar(value=f"Cash: ${self.cash:.2f}")
        self.status_var=tk.StringVar()
        self.net_worth_var=tk.StringVar(value=f"Net Worth: ${self.cash:.2f}")
        self.roi_var=tk.StringVar(value="ROI: +0.00%")

        ttk.Label(self.frm_status,textvariable=self.cash_var,font=self.font_label).pack(side=tk.LEFT,padx=20)
        ttk.Label(self.frm_status,textvariable=self.status_var,font=self.font_label).pack(side=tk.LEFT,fill=tk.X,expand=True)
        ttk.Label(self.frm_status,textvariable=self.net_worth_var,font=self.font_label).pack(side=tk.LEFT,padx=20)
        ttk.Label(self.frm_status,textvariable=self.roi_var,font=self.font_label).pack(side=tk.RIGHT,padx=20)

        self.redraw()
        self.update_ui()

    def on_switch(self):
        self.selected=self.sym_var.get()
        self.redraw()
        self.update_ui()

    def redraw(self):
        self.ax.clear()
        df=self.stocks[self.selected].view()

        mc=mpf.make_marketcolors(up='green',down='red',edge='inherit')
        style=mpf.make_mpf_style(marketcolors=mc)

        mpf.plot(df,type='candle',ax=self.ax,style=style,show_nontrading=False)
        self.ax.set_title(f"{self.selected} - Day {self.stocks[self.selected].current_day+1}",fontsize=16)
        self.canvas.draw()

    def on_next(self):
        active_stock=self.stocks[self.selected]
        if active_stock.current_day>=active_stock.days-1:
            final_net_worth=self.cash+sum(self.portfolio[s]*self.stocks[s].price() for s in self.stocks)
            profit=final_net_worth-self.initial_cash

            messagebox.showinfo("Simulation Complete",f"Game Over!\n\nFinal Net Worth: ${final_net_worth:.2f}\nTotal Profit: ${profit:.2f}")
            return

        for s in self.stocks.values():
            s.advance()
        self.redraw()
        self.update_ui()

    def update_ui(self):
        price=self.stocks[self.selected].price()
        self.price_var.set(f"${price:.2f}")

        total=self.cash+sum(self.portfolio[s]*self.stocks[s].price() for s in self.stocks)
        holdings=[]
        for s,q in self.portfolio.items():
            if q!=0:
                holdings.append(f"{s}:{q:+}")
        
        roi=((total-self.initial_cash)/self.initial_cash)*100
        self.cash_var.set(f"Cash: ${self.cash:.2f}")
        self.status_var.set(f"Portfolio: {', '.join(holdings) or 'None'}")
        self.net_worth_var.set(f"Net Worth: ${total:.2f}")
        self.roi_var.set(f"ROI: {roi:+.2f}%")

    def buy(self):
        try:
            qty=int(self.qty_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid Quantity", "Please Enter a valid Integer Quantity.")
            return
        
        price=self.stocks[self.selected].price()
        cost=price*qty+self.commission_fee

        if qty<=0 or cost>self.cash:
            messagebox.showerror("Error","Invalid Quantity or Insufficient Cash.")
            return

        self.cash-=cost
        self.portfolio[self.selected]+=qty

        self.log_trade(f"Bought {qty} {self.selected} @ ${price:.2f}")
        self.update_ui()

    def sell(self):
        try:
            qty=int(self.qty_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid Quantity", "Please Enter a valid Integer Quantity.")
            return
        
        if qty<=0:
            messagebox.showerror("Error","Quantity must be Positive.")
            return

        price=self.stocks[self.selected].price()
        revenue=price*qty-self.commission_fee
        self.cash+=revenue
        self.portfolio[self.selected]-=qty

        self.log_trade(f"Sold/Shorted {qty} {self.selected} @ ${price:.2f}")
        self.update_ui()

    def log_trade(self,message):
        day=self.stocks[self.selected].current_day+1
        self.log_box.insert(tk.END,f"Day {day}: {message}")
        self.log_box.see(tk.END)

    def on_exit_position(self):
        for s,q in self.portfolio.items():
            price=self.stocks[s].price()
            if q>0:
                self.cash+=q*price-self.commission_fee
                self.portfolio[s]=0
                self.log_trade(f"Sold/Shorted {q} {s} @ ${price:.2f}")

            elif q<0:
                cover=-q
                cost=cover*price
                self.cash-=cost
                self.cash-=self.commission_fee
                self.portfolio[s]=0
                self.log_trade(f"Bought {cover} {s} @ ${price:.2f}")


        self.update_ui()

    def exit_app(self):
        self.quit()
        self.destroy()
