fx_tickers = {

    # 🌍 G10
    "EUR/USD": "EURUSD=X",
    "USD/JPY": "USDJPY=X",
    "GBP/USD": "GBPUSD=X",
    "USD/CHF": "USDCHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",

    # 💵 USD crosses (majeurs)
    "USD/CNY": "USDCNY=X",
    "USD/HKD": "USDHKD=X",
    "USD/SGD": "USDSGD=X",
    "USD/KRW": "USDKRW=X",
    "USD/INR": "USDINR=X",
    "USD/TWD": "USDTWD=X",
    "USD/THB": "USDTHB=X",

    # 🌎 Emerging Markets
    "USD/BRL": "USDBRL=X",
    "USD/MXN": "USDMXN=X",
    "USD/ZAR": "USDZAR=X",
    "USD/TRY": "USDTRY=X",
    "USD/PLN": "USDPLN=X",
    "USD/HUF": "USDHUF=X",
    "USD/CZK": "USDCZK=X",
    "USD/RUB": "USDRUB=X",
    "USD/CLP": "USDCLP=X",
    "USD/COP": "USDCOP=X",
    "USD/PEN": "USDPEN=X",

    # 🛢️ Devises commodities
    "USD/NOK": "USDNOK=X",
    "USD/SEK": "USDSEK=X",
    "USD/DKK": "USDDKK=X",
    "AUD/JPY": "AUDJPY=X",
    "CAD/JPY": "CADJPY=X",
    "NZD/JPY": "NZDJPY=X",

    # 🌍 Europe hors zone euro
    "EUR/CHF": "EURCHF=X",
    "EUR/SEK": "EURSEK=X",
    "EUR/NOK": "EURNOK=X",
    "EUR/PLN": "EURPLN=X",

    # 🌏 Asie
    "EUR/CNY": "EURCNY=X",
    "EUR/INR": "EURINR=X",
    "EUR/KRW": "EURKRW=X",
    "EUR/SGD": "EURSGD=X",

    # 🌍 Moyen-Orient
    "USD/AED": "USDAED=X",
    "USD/SAR": "USDSAR=X",
    "USD/ILS": "USDILS=X",

    # 🌍 Afrique
    "USD/EGP": "USDEGP=X",
    "USD/MAD": "USDMAD=X",
    "USD/NGN": "USDNGN=X"
}

energy_tickers = {

    # 🛢️ Crude Oil
    "Crude Oil WTI": "CL=F",                 # WTI (NYMEX)
    "Brent Crude Oil": "BZ=F",               # Brent
    "Dubai Crude": "DUB=F",                  # Dubai Crude (moins liquide)

    # 🛢️ Refined Products
    "Heating Oil": "HO=F",                   # Fioul domestique
    "RBOB Gasoline": "RB=F",                 # Essence US
    "ULSD Diesel": "ULSD=F",                 # Diesel low sulfur (ICE)

    # 🔥 Natural Gas
    "Natural Gas Henry Hub": "NG=F",         # Gaz US
    "European Natural Gas (TTF)": "TTF=F",   # Gaz Europe
    "UK Natural Gas": "NBP=F",               # Gaz UK
    "Japanese LNG": "JKM=F",                 # LNG Asie (Japon/Korea)

    # ⚡ Electricity
    "PJM Electricity": "PJME=F",             # Électricité US (East)
    "California Electricity": "CAL=F",       # Électricité Californie
    "German Power Baseload": "DEB=F",        # Électricité Allemagne

    # ☢️ Nuclear
    "Uranium": "UX=F",                       # Uranium U3O8

    # 🌱 Carbon & Environmental
    "EU Carbon Allowances": "EUA=F",         # CO2 Europe
    "California Carbon Allowances": "CCA=F", # CO2 Californie
    "RGGI Carbon": "RGGI=F",                 # CO2 US Nord-Est

    # 🌱 Biofuels
    "Ethanol": "EH=F",                       # Ethanol
    "Biodiesel": "BIO=F",                    # Biodiesel (moins liquide)

    # 🌬️ Renewables (certificates / proxies)
    "Renewable Energy Certificates US": "REC=F",
    "Solar Renewable Energy Credits": "SREC=F",

    # ⚙️ Coal
    "Coal API2 (Europe)": "MTF=F",
    "Coal Newcastle (Asia)": "NCL=F"
}

commodities_dict = {
    "Energy": {"Crude Oil": "CL=F", "Natural Gas": "NG=F", "Heating Oil": "HO=F"},
    "Metals": {"Gold": "GC=F", "Silver": "SI=F", "Copper": "HG=F", "Platinum": "PL=F"},
    "Agriculture": {"Corn": "ZC=F", "Wheat": "ZW=F", "Soybeans": "ZS=F", "Coffee": "KC=F"},
    "Livestock": {"Live Cattle": "LE=F", "Lean Hogs": "HE=F"}
}
link_index_ticker = {
    # 🇺🇸 Amérique du Nord
    "S&P 500": "^GSPC",
    "Dow Jones Industrial": "^DJI",
    "NASDAQ Composite": "^IXIC",
    "S&P/TSX Composite (Canada)": "^GSPTSE",

    # 🇪🇺 Europe
    "Euro Stoxx 50": "^STOXX50E",
    "DAX 40 (Allemagne)": "^GDAXI",
    "CAC 40 (France)": "^FCHI",
    "FTSE 100 (Royaume-Uni)": "^FTSE",
    "SMI (Suisse)": "^SSMI",

    # 🌏 Asie
    "Nikkei 225 (Japon)": "^N225",
    "TOPIX (Japon)": "^TOPX",
    "Shanghai Composite (Chine)": "000001.SS",
    "BSE Sensex (Inde)": "^BSESN",
    "KOSPI (Corée)": "^KS11",

    # 🌎 Amérique Latine
    "IBOVESPA (Brésil)": "^BVSP",
    "IPC (Mexique)": "^MXX",
    "MERVAL (Argentine)": "^MERV",
    "IPSA (Chili)": "^IPSA",

    # 🌍 Moyen-Orient / Afrique
    "Tadawul All Share (Arabie Saoudite)": "^TASI",
    "DFM General Index (ÉAU)": "^DFMGI",
    "FTSE/JSE Top 40 (Afrique du Sud)": "^JTOPI",
    "TA-125 (Israël)": "^TA125.TA",

    # 🌐 Indices mondiaux (ETF proxy)
    "MSCI World": "URTH",
    "MSCI Emerging Markets": "EEM",
    "FTSE All-World": "VEU",
    "MSCI Asia ex-Japan": "AAXJ",
    "MSCI Europe": "IEUR"
}

global_equities = {

    # 🇺🇸 USA
    "Apple Inc": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Amazon.com Inc": "AMZN",
    "Alphabet Inc Class A": "GOOGL",
    "Alphabet Inc Class C": "GOOG",
    "Meta Platforms Inc": "META",
    "NVIDIA Corporation": "NVDA",
    "Tesla Inc": "TSLA",
    "Berkshire Hathaway Inc Class B": "BRK-B",
    "JPMorgan Chase & Co": "JPM",
    "Johnson & Johnson": "JNJ",
    "Visa Inc": "V",
    "Mastercard Incorporated": "MA",
    "Exxon Mobil Corporation": "XOM",
    "Chevron Corporation": "CVX",
    "Walmart Inc": "WMT",
    "Procter & Gamble Company": "PG",
    "Coca-Cola Company": "KO",
    "PepsiCo Inc": "PEP",
    "Netflix Inc": "NFLX",
    "Adobe Inc": "ADBE",
    "Salesforce Inc": "CRM",
    "Intel Corporation": "INTC",
    "AMD": "AMD",
    "Qualcomm Inc": "QCOM",
    "PayPal Holdings Inc": "PYPL",
    "Goldman Sachs Group Inc": "GS",
    "Morgan Stanley": "MS",
    "Bank of America Corp": "BAC",

    # 🇫🇷 France
    "TotalEnergies SE": "TTE.PA",
    "Airbus SE": "AIR.PA",
    "LVMH": "MC.PA",
    "L'Oreal": "OR.PA",
    "Sanofi": "SAN.PA",
    "BNP Paribas": "BNP.PA",
    "AXA": "CS.PA",
    "Vinci": "DG.PA",
    "Danone": "BN.PA",
    "Schneider Electric": "SU.PA",
    "Orange SA": "ORA.PA",

    # 🇩🇪 Germany
    "SAP SE": "SAP.DE",
    "Siemens AG": "SIE.DE",
    "Allianz SE": "ALV.DE",
    "Bayer AG": "BAYN.DE",
    "BMW AG": "BMW.DE",
    "Mercedes-Benz Group AG": "MBG.DE",
    "Deutsche Telekom AG": "DTE.DE",

    # 🇬🇧 UK
    "Shell PLC": "SHEL",
    "BP PLC": "BP",
    "HSBC Holdings PLC": "HSBC",
    "Unilever PLC": "UL",
    "AstraZeneca PLC": "AZN",
    "Rio Tinto Group": "RIO",
    "GlaxoSmithKline PLC": "GSK",

    # 🇨🇭 Switzerland
    "Nestle SA": "NESN.SW",
    "Novartis AG": "NOVN.SW",
    "Roche Holding AG": "ROG.SW",
    "UBS Group AG": "UBSG.SW",
    "Zurich Insurance Group": "ZURN.SW",

    # 🇯🇵 Japan
    "Toyota Motor Corporation": "7203.T",
    "Sony Group Corporation": "6758.T",
    "Nintendo Co Ltd": "7974.T",
    "SoftBank Group Corp": "9984.T",
    "Mitsubishi UFJ Financial Group": "8306.T",
    "Hitachi Ltd": "6501.T",

    # 🇨🇳 China
    "Alibaba Group Holding Ltd": "BABA",
    "Tencent Holdings Ltd": "0700.HK",
    "JD.com Inc": "JD",
    "Meituan": "3690.HK",
    "China Construction Bank": "0939.HK",
    "ICBC": "1398.HK",

    # 🇰🇷 Korea
    "Samsung Electronics": "005930.KS",
    "SK Hynix": "000660.KS",
    "LG Energy Solution": "373220.KS",

    # 🇮🇳 India
    "Reliance Industries Ltd": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "Infosys Ltd": "INFY.NS",
    "HDFC Bank Ltd": "HDFCBANK.NS",

    # 🇨🇦 Canada
    "Royal Bank of Canada": "RY",
    "Toronto-Dominion Bank": "TD",
    "Enbridge Inc": "ENB",
    "Shopify Inc": "SHOP",

    # 🇧🇷 Brazil
    "Petroleo Brasileiro SA": "PBR",
    "Vale SA": "VALE",
    "Itau Unibanco Holding": "ITUB",

    # 🇦🇺 Australia
    "BHP Group Ltd": "BHP",
    "Commonwealth Bank of Australia": "CBA.AX",
    "CSL Limited": "CSL.AX"
}
