import streamlit as st
import random

# Dictionary of all financial concepts with their definitions and explanations
CONCEPTS_LIBRARY = {
    # FUNDAMENTAL ANALYSIS
    "Price-to-Earnings Ratio (P/E)": {
        "definition": "Ratio of a company's stock price to its earnings per share. Formula: Market Price per Share / Earnings per Share (EPS)",
        "explanation": "Shows how much investors are willing to pay for each dollar of earnings. High P/E may indicate growth expectations or overvaluation. Low P/E may suggest undervaluation or problems.",
        "category": "Fundamental Analysis",
        "example": "Stock at $100 with EPS of $5 → P/E = 20x. Investors pay $20 for every $1 of earnings."
    },
    "Price-to-Book Ratio (P/B)": {
        "definition": "Ratio of market value to book value (assets minus liabilities). Formula: Market Cap / Book Value",
        "explanation": "P/B < 1 means stock trades below its accounting value (potential value play). P/B > 1 means market values intangibles (brand, IP) highly.",
        "category": "Fundamental Analysis",
        "example": "Company worth $100M on paper but market cap is $80M → P/B = 0.8 (potential undervaluation)"
    },
    "Dividend Yield": {
        "definition": "Annual dividend payment as percentage of stock price. Formula: (Annual Dividend per Share / Price per Share) × 100",
        "explanation": "Shows income return from dividends. High yield may indicate value or distress. Used by income investors. Sustainable yield matters more than high yield.",
        "category": "Fundamental Analysis",
        "example": "Stock at $50 pays $2 annual dividend → Yield = 4%"
    },
    "Return on Equity (ROE)": {
        "definition": "Profitability measure showing how much profit a company generates with shareholders' equity. Formula: Net Income / Shareholders' Equity × 100",
        "explanation": "ROE > 15% is generally good. Shows management efficiency at generating returns. Compare within same industry. High ROE with high debt can be risky.",
        "category": "Fundamental Analysis",
        "example": "Company earns $20M with $100M equity → ROE = 20%"
    },
    "Earnings Per Share (EPS)": {
        "definition": "Company's profit divided by number of outstanding shares. Formula: Net Income / Number of Outstanding Shares",
        "explanation": "Key metric for profitability. Growing EPS = good sign. Used in P/E ratio. Compare quarter-over-quarter and year-over-year.",
        "category": "Fundamental Analysis",
        "example": "$10M profit with 2M shares → EPS = $5 per share"
    },
    "Free Cash Flow (FCF)": {
        "definition": "Cash generated after capital expenditures. Formula: Operating Cash Flow - Capital Expenditures",
        "explanation": "Shows real cash available for dividends, buybacks, or growth. More important than accounting profit. Positive FCF = healthy. Negative = burning cash.",
        "category": "Fundamental Analysis",
        "example": "$50M operating cash - $20M CapEx = $30M FCF available"
    },
    "Debt-to-Equity Ratio": {
        "definition": "Measures financial leverage. Formula: Total Debt / Total Equity",
        "explanation": "Shows how much debt finances the business. D/E > 2 is high (risky in downturns). D/E < 0.5 is conservative. Varies by industry.",
        "category": "Fundamental Analysis",
        "example": "$40M debt with $60M equity → D/E = 0.67"
    },
    "EBITDA": {
        "definition": "Earnings Before Interest, Taxes, Depreciation, and Amortization. Operating performance measure.",
        "explanation": "Shows core profitability before financial engineering. Used to compare companies with different capital structures. Critics say it ignores real costs.",
        "category": "Fundamental Analysis",
        "example": "Revenue $100M - Operating costs $60M = $40M EBITDA"
    },
    
    # MARKET CONCEPTS
    "Market Capitalization": {
        "definition": "Total value of all outstanding shares. Formula: Share Price × Number of Outstanding Shares",
        "explanation": "Size classification: Large-cap (>$10B), Mid-cap ($2-10B), Small-cap ($300M-$2B). Larger = more stable, smaller = more growth potential and risk.",
        "category": "Market Concepts",
        "example": "100M shares at $50 each → Market Cap = $5B (mid-cap)"
    },
    "Liquidity": {
        "definition": "How easily an asset can be bought or sold without affecting its price. High volume = high liquidity.",
        "explanation": "Liquid assets (major stocks, bonds) trade easily. Illiquid assets (real estate, private equity) harder to sell quickly. Liquidity risk increases in crises.",
        "category": "Market Concepts",
        "example": "Apple stock = highly liquid (millions traded daily). Small penny stock = illiquid (hard to sell large blocks)"
    },
    "Bid-Ask Spread": {
        "definition": "Difference between highest price buyer will pay (bid) and lowest price seller will accept (ask).",
        "explanation": "Narrow spread = liquid market, low transaction cost. Wide spread = illiquid, expensive to trade. Market makers profit from the spread.",
        "category": "Market Concepts",
        "example": "Bid $99.50, Ask $100.00 → Spread = $0.50"
    },
    "Market Order vs Limit Order": {
        "definition": "Market Order: Buy/sell immediately at current price. Limit Order: Buy/sell only at specified price or better.",
        "explanation": "Market orders guarantee execution but not price. Limit orders control price but may not execute. Use limits in volatile or illiquid markets.",
        "category": "Market Concepts",
        "example": "Market order in flash crash = bad fill. Limit order at $50 protects but might miss the trade."
    },
    "Short Selling": {
        "definition": "Borrowing shares to sell, hoping to buy back at lower price and profit from decline. Profits from falling prices.",
        "explanation": "Unlimited loss potential (price can rise infinitely). Requires margin account. Short squeeze = rapid price rise forcing shorts to cover at loss.",
        "category": "Market Concepts",
        "example": "Borrow and sell at $100, buy back at $70 → $30 profit per share (minus fees)"
    },
    "Margin Trading": {
        "definition": "Borrowing money from broker to buy securities, using investments as collateral. Amplifies gains AND losses.",
        "explanation": "Initial margin (typically 50% in US). Maintenance margin triggers margin call. Interest charged on borrowed amount. Can lead to forced liquidation.",
        "category": "Market Concepts",
        "example": "$10K cash + $10K borrowed = $20K buying power. 10% gain = $2K profit (20% return on your $10K)"
    },
    "Circuit Breakers": {
        "definition": "Market-wide trading halts triggered by large price declines (7%, 13%, 20% in US) to prevent panic selling.",
        "explanation": "Designed after 1987 crash. Gives investors time to assess. Level 1 (7%) & 2 (13%) = 15min halt. Level 3 (20%) = close for day.",
        "category": "Market Concepts",
        "example": "S&P 500 drops 7% → Trading pauses 15 minutes"
    },
    "Bull Market vs Bear Market": {
        "definition": "Bull Market: Sustained period of rising prices (typically >20% gain). Bear Market: Sustained decline (typically >20% drop).",
        "explanation": "Bull markets driven by optimism, economic growth. Bear markets by pessimism, recession fears. Average bull lasts 4+ years, bear ~1 year.",
        "category": "Market Concepts",
        "example": "2009-2020 = longest bull market in history. 2022 = bear market with 25% decline"
    },
    
    # PORTFOLIO MANAGEMENT
    "Diversification": {
        "definition": "Spreading investments across different assets to reduce risk. 'Don't put all eggs in one basket.'",
        "explanation": "Reduces unsystematic (company-specific) risk. Can't eliminate systematic (market) risk. Optimal is ~20-30 stocks, or index funds for instant diversification.",
        "category": "Portfolio Management",
        "example": "60% stocks, 30% bonds, 10% commodities instead of 100% one stock"
    },
    "Asset Allocation": {
        "definition": "Distribution of portfolio across asset classes (stocks, bonds, cash, real estate, commodities).",
        "explanation": "Single biggest factor in long-term returns (~90%). Adjusted based on risk tolerance, time horizon, goals. Rebalance periodically.",
        "category": "Portfolio Management",
        "example": "Conservative: 40/60 stocks/bonds. Aggressive: 80/20 stocks/bonds"
    },
    "Rebalancing": {
        "definition": "Periodically adjusting portfolio back to target allocation by selling winners and buying losers.",
        "explanation": "Forces 'buy low, sell high' discipline. Prevents overconcentration. Can be calendar-based (annual) or threshold-based (±5%).",
        "category": "Portfolio Management",
        "example": "Target 60/40 stocks/bonds. After rally it's 70/30 → Sell stocks, buy bonds to restore 60/40"
    },
    "Dollar-Cost Averaging (DCA)": {
        "definition": "Investing fixed dollar amount at regular intervals regardless of price. Reduces timing risk.",
        "explanation": "Buys more shares when prices low, fewer when high. Removes emotion from investing. Better than trying to time the market for most investors.",
        "category": "Portfolio Management",
        "example": "Invest $500 monthly: Buy 10 shares at $50, 5 shares at $100 → Average cost $66.67"
    },
    "Modern Portfolio Theory (MPT)": {
        "definition": "Theory by Markowitz stating optimal portfolio maximizes return for given risk level through diversification.",
        "explanation": "Efficient frontier = best risk/return combinations. Importance of correlation between assets. Basis for most institutional portfolio management.",
        "category": "Portfolio Management",
        "example": "Combining uncorrelated assets can increase returns without increasing risk"
    },
    "Risk Tolerance": {
        "definition": "Investor's ability and willingness to withstand losses in pursuit of higher returns.",
        "explanation": "Depends on time horizon, financial situation, personality. Young investors can take more risk (longer recovery time). Conservative = bonds, aggressive = stocks.",
        "category": "Portfolio Management",
        "example": "Retired person = low risk tolerance. 25-year-old = high risk tolerance"
    },
    
    # FIXED INCOME
    "Bond": {
        "definition": "Debt security where investor loans money to borrower (government/corporation) for periodic interest payments and principal repayment at maturity.",
        "explanation": "Safer than stocks but lower returns. Price moves inverse to interest rates. Credit rating indicates default risk. Used for income and stability.",
        "category": "Fixed Income",
        "example": "$1000 bond, 5% coupon, 10 years → Receive $50/year + $1000 at maturity"
    },
    "Yield Curve": {
        "definition": "Graph showing yields of bonds with different maturities. Normal = upward sloping (long-term yields higher).",
        "explanation": "Inverted curve (short-term > long-term) often predicts recession. Flat curve = uncertainty. Steep curve = strong growth expectations.",
        "category": "Fixed Income",
        "example": "2-year Treasury at 2%, 10-year at 4% → Normal upward-sloping curve"
    },
    "Duration": {
        "definition": "Measure of bond's price sensitivity to interest rate changes. Higher duration = more sensitive to rates.",
        "explanation": "Duration ≈ percentage change in bond price for 1% rate change. Long maturity bonds have high duration. Used for interest rate risk management.",
        "category": "Fixed Income",
        "example": "Bond with duration 7 → 1% rate increase = ~7% price decline"
    },
    "Credit Rating": {
        "definition": "Assessment of borrower's creditworthiness by rating agencies (Moody's, S&P, Fitch). AAA = best, D = default.",
        "explanation": "Investment grade: BBB- and above. Junk/high-yield: BB+ and below. Lower rating = higher yield (compensates for risk).",
        "category": "Fixed Income",
        "example": "AAA corporate bond yields 3%, BB bond yields 7% (higher risk premium)"
    },
    "Coupon Rate": {
        "definition": "Annual interest rate paid by bond, expressed as percentage of face value.",
        "explanation": "Fixed at issuance. When market rates rise, existing bonds with low coupons lose value. Zero-coupon bonds pay no interest but sell at deep discount.",
        "category": "Fixed Income",
        "example": "$1000 bond with 5% coupon pays $50/year regardless of market price"
    },
    
    # DERIVATIVES
    "Call Option": {
        "definition": "Contract giving right (not obligation) to BUY asset at specified price (strike) before expiration. Bullish bet.",
        "explanation": "Limited loss (premium paid). Unlimited upside. Used for speculation or hedging. Expires worthless if stock stays below strike.",
        "category": "Derivatives",
        "example": "Buy $100 call for $5. Stock hits $120 → Exercise, profit $15 ($20 gain - $5 premium)"
    },
    "Put Option": {
        "definition": "Contract giving right (not obligation) to SELL asset at specified price before expiration. Bearish bet or insurance.",
        "explanation": "Limited loss (premium). Profits from decline. Used to protect portfolio (protective puts). Expires worthless if stock stays above strike.",
        "category": "Derivatives",
        "example": "Buy $100 put for $5. Stock drops to $80 → Exercise, profit $15 ($20 gain - $5 premium)"
    },
    "Futures Contract": {
        "definition": "Agreement to buy/sell asset at predetermined price on future date. Obligation (unlike options). Standardized and exchange-traded.",
        "explanation": "Used by hedgers and speculators. Marked-to-market daily. High leverage (low margin requirement). Can lose more than initial investment.",
        "category": "Derivatives",
        "example": "Oil futures: Agree today to buy 1000 barrels at $80/barrel in 3 months"
    },
    "Implied Volatility (IV)": {
        "definition": "Market's forecast of future volatility, derived from option prices. High IV = expensive options.",
        "explanation": "IV increases before earnings, events. IV crush = drop after event. Volatility smile = IV varies by strike. Used to compare option prices.",
        "category": "Derivatives",
        "example": "Normal IV 20%, earnings coming → IV jumps to 40% (options more expensive)"
    },
    "Greeks (Options)": {
        "definition": "Risk measures for options: Delta (price sensitivity), Gamma (delta change), Theta (time decay), Vega (volatility sensitivity).",
        "explanation": "Delta 0.5 = option moves $0.50 per $1 stock move. Theta -0.05 = lose $5/day from time decay. Used for hedging and risk management.",
        "category": "Derivatives",
        "example": "Delta 0.70 means option behaves like 70 shares of stock"
    },
    
    # MACROECONOMICS
    "Gross Domestic Product (GDP)": {
        "definition": "Total value of all goods and services produced in country during period. Primary measure of economic health.",
        "explanation": "GDP growth >3% = strong. <0% = recession. Real GDP adjusted for inflation. GDP per capita = standard of living. Reported quarterly.",
        "category": "Macroeconomics",
        "example": "US GDP ~$25 trillion. 2% annual growth = $500B increase in economic output"
    },
    "Inflation": {
        "definition": "Rate at which general price level increases, eroding purchasing power. Measured by CPI, PCE.",
        "explanation": "Moderate inflation (2-3%) considered healthy. High inflation (>5%) hurts consumers. Deflation (negative) can be worse. Fed targets 2%.",
        "category": "Macroeconomics",
        "example": "4% inflation means $100 today buys only $96 worth of goods next year"
    },
    "Interest Rates": {
        "definition": "Cost of borrowing money, set by central banks (Fed in US). Key policy tool for managing economy.",
        "explanation": "High rates = slow borrowing/spending (fight inflation). Low rates = encourage borrowing/growth. Affects bonds, stocks, currency, real estate.",
        "category": "Macroeconomics",
        "example": "Fed raises rates from 2% to 5% → Mortgages more expensive, stocks often decline"
    },
    "Federal Reserve (The Fed)": {
        "definition": "US central bank controlling monetary policy. Sets interest rates, regulates banks, manages money supply.",
        "explanation": "Dual mandate: Maximum employment + stable prices. FOMC meets 8x/year. Tools: interest rates, QE/QT, reserve requirements.",
        "category": "Macroeconomics",
        "example": "Fed cuts rates in recession to stimulate economy. Raises rates when inflation too high."
    },
    "Quantitative Easing (QE)": {
        "definition": "Central bank buying government bonds/securities to inject money into economy and lower long-term rates.",
        "explanation": "Used when normal rate cuts insufficient (near zero). Inflates asset prices. Opposite = Quantitative Tightening (QT). Controversial policy.",
        "category": "Macroeconomics",
        "example": "Fed bought $4 trillion bonds 2008-2014 to combat financial crisis"
    },
    "Unemployment Rate": {
        "definition": "Percentage of labor force actively seeking work but unable to find jobs.",
        "explanation": "Low unemployment (<4%) = strong economy. High (>7%) = weak. 'Natural rate' ~5%. U3 (official) vs U6 (includes underemployed).",
        "category": "Macroeconomics",
        "example": "Unemployment 3.5% = full employment. 10% = severe recession"
    },
    "Fiscal Policy": {
        "definition": "Government use of spending and taxation to influence economy. Complementary to monetary policy.",
        "explanation": "Expansionary: Increase spending/cut taxes (stimulus). Contractionary: Decrease spending/raise taxes. Can lead to deficits. Political process.",
        "category": "Macroeconomics",
        "example": "2020 COVID stimulus: Government spending trillions to support economy"
    },
    "Trade Balance": {
        "definition": "Difference between country's exports and imports. Surplus = exports > imports. Deficit = imports > exports.",
        "explanation": "Persistent deficits can pressure currency. Not necessarily bad (might reflect strong economy). Part of current account.",
        "category": "Macroeconomics",
        "example": "US imports $3T, exports $2T → $1T trade deficit"
    },
    
    # BEHAVIORAL FINANCE
    "Loss Aversion": {
        "definition": "Psychological principle that losses hurt more than equivalent gains feel good (by ~2x factor).",
        "explanation": "Causes investors to hold losers too long, sell winners too early. Prevents rational decision-making. Explains why people avoid necessary losses.",
        "category": "Behavioral Finance",
        "example": "Losing $100 feels worse than joy of gaining $100. Leads to 'get-even-itis' in bad trades."
    },
    "Confirmation Bias": {
        "definition": "Tendency to seek information that confirms existing beliefs while ignoring contradictory evidence.",
        "explanation": "Makes investors ignore warnings. Creates echo chambers. Overcome by actively seeking opposite viewpoints. Devil's advocate approach helps.",
        "category": "Behavioral Finance",
        "example": "Bullish on stock → Only read positive articles, dismiss negative news as 'FUD'"
    },
    "Herd Mentality": {
        "definition": "Following the crowd's investment decisions rather than independent analysis. FOMO-driven behavior.",
        "explanation": "Leads to bubbles (everyone buying) and crashes (everyone selling). 'Be fearful when others are greedy.' Contrarian strategy exploits this.",
        "category": "Behavioral Finance",
        "example": "2021 meme stocks: Buying because 'everyone is making money' → Leads to crashes"
    },
    "Anchoring": {
        "definition": "Over-reliance on first piece of information encountered (the 'anchor') when making decisions.",
        "explanation": "Investors anchor to purchase price. 'Stock was $100 so $80 is cheap' (ignoring fundamentals changed). Affects sell decisions.",
        "category": "Behavioral Finance",
        "example": "Bought at $50, now $40. Waiting to 'break even' at $50 instead of evaluating current merit."
    },
    "Recency Bias": {
        "definition": "Giving more weight to recent events than historical data. Believing recent trends will continue.",
        "explanation": "Bull market → Everyone thinks stocks only go up. Causes poor market timing. Overcome by studying full market cycles.",
        "category": "Behavioral Finance",
        "example": "2020-2021 tech gains → 'Tech always wins' → Surprised by 2022 crash"
    },
    "Overconfidence": {
        "definition": "Overestimating one's knowledge, ability to predict outcomes, or control over events.",
        "explanation": "Leads to excessive trading, concentrated positions, ignoring risks. Men often more overconfident than women. Causes underestimation of downside.",
        "category": "Behavioral Finance",
        "example": "Day trader: '10 winning trades proves my skill' (ignoring luck, survivorship bias)"
    },
    
    # MARKET EFFICIENCY
    "Efficient Market Hypothesis (EMH)": {
        "definition": "Theory that asset prices fully reflect all available information. Three forms: weak, semi-strong, strong.",
        "explanation": "If true, impossible to beat market consistently. Weak form = can't profit from past prices. Strong = no one can beat market. Controversial.",
        "category": "Market Efficiency",
        "example": "News about company instantly reflected in price → Can't profit from public info"
    },
    "Random Walk Theory": {
        "definition": "Theory that stock price changes are random and unpredictable, like a drunk person's walk.",
        "explanation": "Supports EMH. Past prices don't predict future. Technical analysis useless if true. Basis for passive investing.",
        "category": "Market Efficiency",
        "example": "Today's price up/down tells nothing about tomorrow → Can't predict chart patterns"
    },
    "Market Anomalies": {
        "definition": "Patterns that contradict EMH and appear exploitable: size effect, value premium, momentum, January effect.",
        "explanation": "Small-cap outperformance, value beats growth long-term, winners keep winning. Anomalies often disappear once discovered.",
        "category": "Market Efficiency",
        "example": "January effect: Stocks often rally in January (tax-loss harvesting reversal)"
    },
    
    # VALUATION
    "Intrinsic Value": {
        "definition": "Theoretical 'true' value of asset based on fundamental analysis, independent of market price.",
        "explanation": "Calculated via DCF, multiples, or other models. Value investing = buy when price < intrinsic value. Subjective (depends on assumptions).",
        "category": "Valuation",
        "example": "DCF suggests stock worth $80. Currently $50 → Undervalued, buy opportunity"
    },
    "Discounted Cash Flow (DCF)": {
        "definition": "Valuation method calculating present value of expected future cash flows using discount rate (WACC).",
        "explanation": "Core valuation technique. Sensitive to assumptions (growth, discount rate). Time value of money: $1 today > $1 tomorrow.",
        "category": "Valuation",
        "example": "Future $100 discounted at 10% = $90.91 present value"
    },
    "Enterprise Value (EV)": {
        "definition": "Total value of company: Market Cap + Debt - Cash. More accurate than market cap alone for acquisitions.",
        "explanation": "EV/EBITDA common valuation multiple. Takes capital structure into account. Used in M&A. Debt must be paid by acquirer.",
        "category": "Valuation",
        "example": "$100M market cap + $30M debt - $10M cash = $120M EV"
    },
    "PEG Ratio": {
        "definition": "P/E ratio divided by earnings growth rate. Adjusts P/E for growth. PEG < 1 potentially undervalued.",
        "explanation": "P/E of 30 seems high, but with 30% growth → PEG = 1 (fair). Accounts for different growth rates. Growth must be sustainable.",
        "category": "Valuation",
        "example": "P/E 25, EPS growth 25% → PEG = 1.0 (fairly valued for growth)"
    },
    
    # RISK CONCEPTS
    "Systematic Risk": {
        "definition": "Market-wide risk affecting all securities (recession, interest rates, inflation). Cannot be diversified away.",
        "explanation": "Also called market risk or undiversifiable risk. Measured by beta. Only way to reduce is lower equity allocation.",
        "category": "Risk Concepts",
        "example": "2008 crisis: Almost all stocks fell together (systematic risk event)"
    },
    "Unsystematic Risk": {
        "definition": "Company-specific risk (management, product failure, lawsuit). Can be eliminated through diversification.",
        "explanation": "Also called idiosyncratic or diversifiable risk. Reason to hold multiple stocks. Disappears in well-diversified portfolio.",
        "category": "Risk Concepts",
        "example": "CEO scandal at one company doesn't affect other holdings (diversification protects)"
    },
    "Liquidity Risk": {
        "definition": "Risk of being unable to sell asset quickly without significant price concession.",
        "explanation": "High in illiquid assets (real estate, private equity, micro-caps). Increases in crises. Wide bid-ask spread signals liquidity risk.",
        "category": "Risk Concepts",
        "example": "2008: Even AAA bonds couldn't be sold at reasonable prices (liquidity crisis)"
    },
    "Credit Risk": {
        "definition": "Risk that borrower will default on debt obligations. Higher for lower-rated bonds and loans.",
        "explanation": "Compensated by higher yield (credit spread). Increases in recessions. Can diversify but not eliminate. Rating agencies assess credit risk.",
        "category": "Risk Concepts",
        "example": "Junk bonds yield 8% vs Treasury 3% → 5% credit spread for default risk"
    },
    "Currency Risk": {
        "definition": "Risk that exchange rate changes will negatively affect investment returns. Relevant for international investing.",
        "explanation": "Foreign stock up 10% but currency down 15% → Net loss 5%. Can hedge with currency forwards. Diversification can help.",
        "category": "Risk Concepts",
        "example": "European stock gains 20% in euros, but euro falls 10% vs dollar → Only 8% gain for US investor"
    },
    "Black Swan Event": {
        "definition": "Extremely rare, unpredictable event with massive impact. Popularized by Nassim Taleb.",
        "explanation": "Examples: 9/11, 2008 crisis, COVID. Normal models underestimate. Fat tails in return distributions. Importance of tail risk hedging.",
        "category": "Risk Concepts",
        "example": "COVID pandemic: 'Once in 100 years' event causing market crash"
    }
}

def initialize_concepts_session_state():
    """Initialize session state variables for the concepts quiz"""
    if 'concepts_quiz_started' not in st.session_state:
        st.session_state.concepts_quiz_started = False
    if 'current_concept' not in st.session_state:
        st.session_state.current_concept = None
    if 'concepts_score' not in st.session_state:
        st.session_state.concepts_score = 0
    if 'concepts_total_questions' not in st.session_state:
        st.session_state.concepts_total_questions = 0
    if 'concepts_show_answer' not in st.session_state:
        st.session_state.concepts_show_answer = False
    if 'used_concepts' not in st.session_state:
        st.session_state.used_concepts = []
    if 'concepts_user_guess' not in st.session_state:
        st.session_state.concepts_user_guess = ""

def get_random_concept():
    """Get a random concept that hasn't been used yet"""
    available_concepts = [c for c in CONCEPTS_LIBRARY.keys() if c not in st.session_state.used_concepts]
    
    if not available_concepts:
        # Reset if all concepts have been used
        st.session_state.used_concepts = []
        available_concepts = list(CONCEPTS_LIBRARY.keys())
    
    concept = random.choice(available_concepts)
    st.session_state.used_concepts.append(concept)
    return concept

def display_concepts_quiz():
    st.title("💼 Financial Concepts Quiz")
    st.markdown("### Master the essential concepts of finance and investing!")
    
    # Display score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{st.session_state.concepts_score}")
    with col2:
        st.metric("Questions", f"{st.session_state.concepts_total_questions}")
    with col3:
        accuracy = (st.session_state.concepts_score / st.session_state.concepts_total_questions * 100) if st.session_state.concepts_total_questions > 0 else 0
        st.metric("Accuracy", f"{accuracy:.1f}%")
    
    st.divider()
    
    # Start quiz button
    if not st.session_state.concepts_quiz_started:
        if st.button("🚀 Start Quiz", use_container_width=True, type="primary"):
            st.session_state.concepts_quiz_started = True
            st.session_state.current_concept = get_random_concept()
            st.session_state.concepts_show_answer = False
            st.rerun()
    
    # Quiz interface
    if st.session_state.concepts_quiz_started and st.session_state.current_concept:
        concept_name = st.session_state.current_concept
        concept_data = CONCEPTS_LIBRARY[concept_name]
        
        # Display the concept name in a nice box
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        ">
            <h1 style="
                color: white;
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            ">💡 {concept_name}</h1>
            <p style="
                color: rgba(255,255,255,0.9);
                margin-top: 10px;
                font-size: 1.1em;
            ">Explain this financial concept</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User input area
        if not st.session_state.concepts_show_answer:
            st.markdown("### What is this concept?")
            user_answer = st.text_area(
                "Write your answer here...",
                height=150,
                placeholder="Explain what this concept means, why it's important, and how it's used in finance...",
                key="concepts_answer_input"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_a:
                if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
                    if user_answer.strip():
                        st.session_state.concepts_user_guess = user_answer
                        st.session_state.concepts_show_answer = True
                        st.session_state.concepts_total_questions += 1
                        st.rerun()
                    else:
                        st.warning("Please write an answer first!")
            
            with col_b:
                if st.button("💡 Show Answer", use_container_width=True):
                    st.session_state.concepts_show_answer = True
                    st.session_state.concepts_total_questions += 1
                    st.rerun()
            
            with col_c:
                if st.button("⏭️ Skip", use_container_width=True):
                    st.session_state.current_concept = get_random_concept()
                    st.session_state.concepts_show_answer = False
                    st.rerun()
        
        # Show answer section
        if st.session_state.concepts_show_answer:
            st.markdown("---")
            
            # Show user's answer if they submitted one
            if st.session_state.concepts_user_guess:
                st.markdown("### Your Answer:")
                st.info(st.session_state.concepts_user_guess)
            
            # Show correct answer
            st.markdown("### 📚 Correct Answer:")
            
            st.markdown(f"**Category:** `{concept_data['category']}`")
            
            with st.expander("📖 Definition", expanded=True):
                st.write(concept_data['definition'])
            
            with st.expander("🎯 Explanation & Importance", expanded=True):
                st.write(concept_data['explanation'])
            
            with st.expander("💼 Real-World Example", expanded=True):
                st.write(concept_data['example'])
            
            st.markdown("---")
            
            # Self-assessment
            st.markdown("### How did you do?")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ I got it right!", use_container_width=True, type="primary"):
                    st.session_state.concepts_score += 1
                    st.session_state.current_concept = get_random_concept()
                    st.session_state.concepts_show_answer = False
                    st.session_state.concepts_user_guess = ""
                    st.balloons()
                    st.rerun()
            
            with col2:
                if st.button("❌ I was wrong", use_container_width=True):
                    st.session_state.current_concept = get_random_concept()
                    st.session_state.concepts_show_answer = False
                    st.session_state.concepts_user_guess = ""
                    st.rerun()
            
            with col3:
                if st.button("➡️ Next Question", use_container_width=True):
                    st.session_state.current_concept = get_random_concept()
                    st.session_state.concepts_show_answer = False
                    st.session_state.concepts_user_guess = ""
                    st.rerun()
    
    # Sidebar with study guide
    with st.sidebar:
        st.markdown("## 📚 Study Guide")
        
        category_filter = st.selectbox(
            "Filter by category",
            ["All"] + sorted(list(set(c['category'] for c in CONCEPTS_LIBRARY.values())))
        )
        
        st.markdown("---")
        
        for concept, data in sorted(CONCEPTS_LIBRARY.items()):
            if category_filter == "All" or data['category'] == category_filter:
                with st.expander(f"💼 {concept}"):
                    st.markdown(f"**Category:** {data['category']}")
                    st.markdown(f"**Definition:** {data['definition']}")
                    st.markdown(f"**Example:** {data['example']}")
        
        st.markdown("---")
        
        # Statistics
        if st.session_state.concepts_total_questions > 0:
            st.markdown("### 📊 Your Progress")
            categories_tested = {}
            for concept in st.session_state.used_concepts:
                if concept in CONCEPTS_LIBRARY:
                    cat = CONCEPTS_LIBRARY[concept]['category']
                    categories_tested[cat] = categories_tested.get(cat, 0) + 1
            
            for cat, count in sorted(categories_tested.items()):
                st.text(f"{cat}: {count} questions")
        
        st.markdown("---")
        if st.button("🔄 Reset Quiz", use_container_width=True):
            st.session_state.concepts_quiz_started = False
            st.session_state.current_concept = None
            st.session_state.concepts_score = 0
            st.session_state.concepts_total_questions = 0
            st.session_state.concepts_show_answer = False
            st.session_state.used_concepts = []
            st.session_state.concepts_user_guess = ""
            st.rerun()
