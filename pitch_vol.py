#%%
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#%% Page 1
sp=yf.Ticker("SPY")
vix=yf.Ticker("^VIX")
vst=yf.Ticker("V2TX.DE")

#Mandat trump : 20 janvier 2025 -20 janvier 2029
start = pd.Timestamp("2025-04-02").tz_localize('America/New_York')
# Affichage de la vol :
period=vix.history(period="2y").loc["2025-01-01":"2026-01-01","Close"]
plt.plot(period,label="VIX Close")
plt.plot(start,period.loc[start],"o",color="red")
plt.title("Vix")
plt.xlabel("Date")
plt.ylabel("Value")
plt.show()

# Affichage SP500 :
period1=sp.history(period="2y").loc["2025-01-01":"2026-01-01","Close"]
plt.plot(period1,label="SP500 Close")
plt.plot(start,period1.loc[start],"o",color="red")
#print(period1.idxmin(),period1.min())
plt.title("SP500")
plt.xlabel("Date")
plt.ylabel("Value")
plt.show()





# la vol à évoluer de tant de % en % :
min_date=vix.history(period="2y").loc[start-pd.DateOffset(days=10):start,"Close"].idxmin()
max_date=vix.history(period="2y").loc[start:start+pd.DateOffset(days=10),"Close"].idxmax()
min_value=vix.history(period="2y").loc[min_date,"Close"]
max_value=vix.history(period="2y").loc[max_date,"Close"]
min_value1=sp.history(period="2y").loc[max_date,"Close"]
plt.plot(vix.history(period="2y").loc[start-pd.DateOffset(days=10):start+pd.DateOffset(days=10),"Close"])
plt.plot(min_date,min_value,"o",color="red")
plt.plot(max_date,max_value,"o",color="red")
plt.show()
print(min_date,min_value)
print(max_date,max_value)
print("Ecolution en % de la valeur du VIX ",((max_value-min_value)/min_value)*100)

max_date1=sp.history(period="2y").loc[start-pd.DateOffset(days=10):start,"Close"].idxmax()
min_date1=sp.history(period="2y").loc[start:start+pd.DateOffset(days=10),"Close"].idxmin()
max_value1=sp.history(period="2y").loc[min_date,"Close"]
min_value1=sp.history(period="2y").loc[max_date,"Close"]
#plt.plot(sp.history(period="2y").loc[start-pd.DateOffset(days=10):start+pd.DateOffset(days=10),"Close"])
#plt.plot(min_date1,min_value1,"o",color="red")
#plt.plot(max_date1,max_value1,"o",color="red")
#print(min_date,min_value)
#print(max_date,max_value)
print("Ecolution en % de la valeur du SP ",(((min_value1 - max_value1) / max_value1) * 100))

# Maxdrawdown
series = period.loc[start-pd.DateOffset(days=10):start+pd.DateOffset(days=10)]
series1=period1.loc[start-pd.DateOffset(days=10):start+pd.DateOffset(days=10)]
cum_max = series.cummax()
cum_max1=series1.cummax()
drawdown = (series - cum_max) / cum_max 
drawdown1 = (series1 - cum_max1) / cum_max1 
max_dd = drawdown.min()
max_dd1 = drawdown1.min()
end_date = drawdown.idxmin() 
end_date1 = drawdown1.idxmin() 
start_date = series.loc[:end_date].idxmax()  
start_date1 = series1.loc[:end_date1].idxmax()  

print(f"Max Drawdown VIX : {max_dd*100:.2f}%")
print(f"Du {start_date} au {end_date}")
print(f"Max Drawdown SP500: {max_dd1*100:.2f}%")
print(f"Du {start_date1} au {end_date1}")


#Corrélations 
return_sp=period1.pct_change()
return_vix=period.pct_change()
corr = return_sp.corr(return_vix)
print(f"Corrélation rendements SP500/VIX : {corr:.2f}")


#%% Page 2 :
#Mandat trump : 20 janvier 2025 -20 janvier 2029
# Dates
start = pd.Timestamp("2025-01-20").tz_localize('America/New_York')
end = pd.Timestamp("2026-01-01").tz_localize('America/New_York')

# Récupérer les prix
echantillon = sp.history(period="2y").loc[start:end, "Close"]

# Rendements journaliers logarithmiques
returns = np.log(echantillon / echantillon.shift(1)).dropna()

# Paramètres
facteur_annualisation = 252
Nominal_var = 250000
var_strike = 0.2**2

# Variance réalisée cumulative (moyenne des carrés jusqu'à chaque jour)
var_real_cumul = facteur_annualisation * (returns**2).expanding().mean()

# Payoff quotidien
payoff = Nominal_var * (var_real_cumul - var_strike)

# Affichage
plt.plot(payoff)
plt.title("Evolution of the var swap payoff")
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Day")
plt.ylabel("Payoff ($)")
plt.grid(True)
plt.show()

# Paramètres
Nominal_var = 250_000        # Notional du swap
var_strike = 0.2**2          # Strike variance = 20%^2
vol_real = np.linspace(0.10, 0.40, 100)  # Volatilité réalisée de 10% à 40%

# Variance réalisée correspondante
var_realized = vol_real**2

# Payoff du variance swap
payoff = Nominal_var * (var_realized - var_strike)

# Affichage
plt.figure(figsize=(8,5))
plt.plot(vol_real*100, payoff, color='blue', lw=2)
plt.axhline(0, color='red', linestyle='--')
plt.title("Payoff of the variance swap based on volatility")
plt.xlabel("Daily volatility (%)")
plt.ylabel("Payoff ($)")
plt.grid(True)
plt.legend()
plt.show()
