import streamlit as st
import random
from datetime import datetime

# Dictionary of all metrics with their definitions and interpretations
METRICS_LIBRARY = {
    "Sharpe Ratio": {
        "definition": "Risk-adjusted return metric measuring excess return per unit of total volatility. Formula: $SR = \\frac{R_p - R_f}{\\sigma_p}$",
        "interpretation": "Higher is better. Above 1.0 is good, 2.0 very good. Tells you if returns justify the total risk taken.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 1.0"
    },
    "Sortino Ratio": {
        "definition": "Similar to Sharpe but only penalizes downside volatility (negative returns). Formula: $Sortino = \\frac{R_p - R_f}{\\sigma_{down}}$",
        "interpretation": "More relevant for investors who don't mind upside volatility. Higher values indicate better downside-adjusted performance.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 1.5"
    },
    "Calmar Ratio": {
        "definition": "Measures return relative to maximum drawdown, usually over a 3-year period. Formula: $Calmar = \\frac{\\text{Annualized Return}}{|\\text{Max Drawdown}|}$",
        "interpretation": "Shows return vs. worst-case loss scenario. Higher is better. Focuses on the medium-term recovery potential.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 0.5"
    },
    "MAR Ratio": {
        "definition": "Similar to Calmar but uses the Maximum Drawdown since inception. Formula: $MAR = \\frac{\\text{CAGR}}{|\\text{Max Drawdown}_{total}|}$",
        "interpretation": "Standard for hedge funds to compare long-term growth against the worst historical drop.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 0.5"
    },
    "Treynor Ratio": {
        "definition": "Risk-adjusted return using systematic risk (beta) instead of total risk. Formula: $Treynor = \\frac{R_p - R_f}{\\beta_p}$",
        "interpretation": "Useful for comparing diversified portfolios. Shows return per unit of market risk taken.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 0.05"
    },
    "Information Ratio": {
        "definition": "Measures risk-adjusted excess returns relative to a benchmark. Formula: $IR = \\frac{R_p - R_b}{\\text{Tracking Error}}$",
        "interpretation": "Shows if active management adds value consistently. IR > 0.5 is good. Indicates manager skill.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 0.5"
    },
    "Omega Ratio": {
        "definition": "Ratio of probability-weighted gains to probability-weighted losses relative to a target return.",
        "interpretation": "Considers the full return distribution (including skewness/kurtosis). Omega > 1 means gains outweigh losses.",
        "category": "Risk-Adjusted Returns",
        "good_range": "> 1.2"
    },
    "Maximum Drawdown (MDD)": {
        "definition": "The largest peak-to-trough decline in asset value during a specific period. Expressed as a percentage.",
        "interpretation": "Lower is better. Shows the worst-case loss an investor would have experienced.",
        "category": "Risk Metrics",
        "good_range": "< 20%"
    },
    "Volatility": {
        "definition": "Standard deviation of returns ($\sigma$), typically annualized. Measures the dispersion of returns around the mean.",
        "interpretation": "Lower = more stable. High = higher uncertainty. Typically 15-25% for equities.",
        "category": "Risk Metrics",
        "good_range": "10-20%"
    },
    "Downside Deviation": {
        "definition": "Standard deviation of only negative returns (below a threshold, often 0% or risk-free rate).",
        "interpretation": "Focuses only on 'bad' risk. Used in the Sortino Ratio calculation. Lower is better.",
        "category": "Risk Metrics",
        "good_range": "< 10%"
    },
    "Ulcer Index": {
        "definition": "Measures depth and duration of drawdowns. Formula: $\\sqrt{\\text{mean}(\\text{drawdowns}^2)}$.",
        "interpretation": "Lower is better. Captures the 'psychological pain' of holding losing positions over time.",
        "category": "Risk Metrics",
        "good_range": "< 10%"
    },
    "Value at Risk (VaR)": {
        "definition": "The maximum expected loss over a given time at a specific confidence level (e.g., 95%).",
        "interpretation": "A 95% VaR of -3% means there's a 5% chance of losing more than 3% in a single period.",
        "category": "Risk Metrics",
        "good_range": "Relative to risk appetite"
    },
    "Conditional VaR (CVaR)": {
        "definition": "Also called Expected Shortfall. The average loss in the worst X% of cases (beyond the VaR threshold).",
        "interpretation": "Captures 'tail risk'. Shows what happens in extreme crash scenarios. Always worse than VaR.",
        "category": "Risk Metrics",
        "good_range": "Monitor with VaR"
    },
    "Tracking Error": {
        "definition": "Standard deviation of the difference between portfolio returns and benchmark returns.",
        "interpretation": "Measures how closely a portfolio follows its benchmark. High = active management.",
        "category": "Risk Metrics",
        "good_range": "< 5% (Passive)"
    },
    "Skewness": {
        "definition": "Measures the asymmetry of return distribution. Negative skew = frequent small gains/rare large losses.",
        "interpretation": "Investors prefer positive skew. Significant negative skew indicates 'tail risk' of crashes.",
        "category": "Distribution Metrics",
        "good_range": "> 0"
    },
    "Kurtosis": {
        "definition": "Measures the 'fatness' of distribution tails. Excess kurtosis compares the distribution to a normal curve.",
        "interpretation": "High kurtosis (>3) means extreme events (outliers) happen more often than expected.",
        "category": "Distribution Metrics",
        "good_range": "Close to 3 (or 0 excess)"
    },
    "Annualized Return": {
        "definition": "The geometric average return per year (CAGR). Accounts for compounding.",
        "interpretation": "Shows average yearly growth. 7-10% is historically typical for equities.",
        "category": "Performance Metrics",
        "good_range": "> 8%"
    },
    "Win Rate": {
        "definition": "Percentage of periods (days/months) with positive returns.",
        "interpretation": "Higher is more consistent, but doesn't account for the size of the wins vs losses.",
        "category": "Performance Metrics",
        "good_range": "> 55%"
    },
    "Profit Factor": {
        "definition": "Ratio of gross profits to gross losses. Formula: $\\frac{\\sum \\text{Wins}}{|\\sum \\text{Losses}|}$",
        "interpretation": "> 1.0 is profitable. > 2.0 is excellent. Shows if wins are large enough to cover losses.",
        "category": "Performance Metrics",
        "good_range": "> 1.5"
    },
    "Recovery Factor": {
        "definition": "Net profit divided by maximum drawdown. Measures profit per unit of historical risk.",
        "interpretation": "Higher is better. Recovery Factor > 3.0 is generally considered strong.",
        "category": "Performance Metrics",
        "good_range": "> 3.0"
    },
    "Beta": {
        "definition": "Sensitivity to market movements. Formula: $\\beta = \\frac{Cov(R_p, R_m)}{Var(R_m)}$",
        "interpretation": "Beta 1 = moves with market. > 1 = aggressive. < 1 = defensive.",
        "category": "Relative Metrics",
        "good_range": "0.8 - 1.2"
    },
    "Alpha": {
        "definition": "Excess return above the expected return given the beta (CAPM).",
        "interpretation": "Positive alpha = outperformance due to manager skill.",
        "category": "Relative Metrics",
        "good_range": "> 0%"
    },
    "Capture Ratio": {
        "definition": "Ratio of fund returns to market returns during up/down periods.",
        "interpretation": "Up-capture > 100 and Down-capture < 100 is the ideal profile.",
        "category": "Relative Metrics",
        "good_range": "Up > Down"
    },
    "R-Squared ($R^2$)": {
        "definition": "Percentage of a fund's movements that can be explained by movements in its benchmark.",
        "interpretation": "High $R^2$ (85-100%) means the Beta is reliable. Low means other factors drive returns.",
        "category": "Relative Metrics",
        "good_range": "> 0.85"
    },
    "Relative Strength Index (RSI)": {
        "definition": "Momentum oscillator measuring the speed and change of price movements.",
        "interpretation": "> 70 is overbought (potential drop). < 30 is oversold (potential bounce).",
        "category": "Technical Indicators",
        "good_range": "30 - 70"
    }
}


def initialize_session_state():
    """Initialize session state variables for the quiz"""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'current_metric' not in st.session_state:
        st.session_state.current_metric = None
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'used_metrics' not in st.session_state:
        st.session_state.used_metrics = []
    if 'user_guess' not in st.session_state:
        st.session_state.user_guess = ""

def get_random_metric():
    """Get a random metric that hasn't been used yet"""
    available_metrics = [m for m in METRICS_LIBRARY.keys() if m not in st.session_state.used_metrics]
    
    if not available_metrics:
        # Reset if all metrics have been used
        st.session_state.used_metrics = []
        available_metrics = list(METRICS_LIBRARY.keys())
    
    metric = random.choice(available_metrics)
    st.session_state.used_metrics.append(metric)
    return metric

def display_quiz():
    st.title("📊 Financial Metrics Quiz")
    st.markdown("### Test your knowledge of financial analysis metrics!")
    
    # Display score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{st.session_state.score}")
    with col2:
        st.metric("Questions", f"{st.session_state.total_questions}")
    with col3:
        accuracy = (st.session_state.score / st.session_state.total_questions * 100) if st.session_state.total_questions > 0 else 0
        st.metric("Accuracy", f"{accuracy:.1f}%")
    
    st.divider()
    
    # Start quiz button
    if not st.session_state.quiz_started:
        if st.button("🚀 Start Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_started = True
            st.session_state.current_metric = get_random_metric()
            st.session_state.show_answer = False
            st.rerun()
    
    # Quiz interface
    if st.session_state.quiz_started and st.session_state.current_metric:
        metric_name = st.session_state.current_metric
        metric_data = METRICS_LIBRARY[metric_name]
        
        # Display the metric name in a nice box
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
            ">❓ {metric_name}</h1>
            <p style="
                color: rgba(255,255,255,0.9);
                margin-top: 10px;
                font-size: 1.1em;
            ">What does this metric measure?</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User input area
        if not st.session_state.show_answer:
            st.markdown("### What is this metric?")
            user_answer = st.text_area(
                "Write your answer here...",
                height=150,
                placeholder="Explain what this metric measures, what it's used for, and how to interpret it...",
                key="answer_input"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_a:
                if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
                    if user_answer.strip():
                        st.session_state.user_guess = user_answer
                        st.session_state.show_answer = True
                        st.session_state.total_questions += 1
                        st.rerun()
                    else:
                        st.warning("Please write an answer first!")
            
            with col_b:
                if st.button("💡 Show Answer", use_container_width=True):
                    st.session_state.show_answer = True
                    st.session_state.total_questions += 1
                    st.rerun()
            
            with col_c:
                if st.button("⏭️ Skip", use_container_width=True):
                    st.session_state.current_metric = get_random_metric()
                    st.session_state.show_answer = False
                    st.rerun()
        
        # Show answer section
        if st.session_state.show_answer:
            st.markdown("---")
            
            # Show user's answer if they submitted one
            if st.session_state.user_guess:
                st.markdown("### Your Answer:")
                st.info(st.session_state.user_guess)
            
            # Show correct answer
            st.markdown("### 📚 Correct Answer:")
            
            st.markdown(f"**Category:** `{metric_data['category']}`")
            
            with st.expander("📖 Definition", expanded=True):
                st.write(metric_data['definition'])
            
            with st.expander("🎯 Interpretation", expanded=True):
                st.write(metric_data['interpretation'])
            
            with st.expander("✨ Good Range", expanded=True):
                st.write(metric_data['good_range'])
            
            st.markdown("---")
            
            # Self-assessment
            st.markdown("### How did you do?")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ I got it right!", use_container_width=True, type="primary"):
                    st.session_state.score += 1
                    st.session_state.current_metric = get_random_metric()
                    st.session_state.show_answer = False
                    st.session_state.user_guess = ""
                    st.balloons()
                    st.rerun()
            
            with col2:
                if st.button("❌ I was wrong", use_container_width=True):
                    st.session_state.current_metric = get_random_metric()
                    st.session_state.show_answer = False
                    st.session_state.user_guess = ""
                    st.rerun()
            
            with col3:
                if st.button("➡️ Next Question", use_container_width=True):
                    st.session_state.current_metric = get_random_metric()
                    st.session_state.show_answer = False
                    st.session_state.user_guess = ""
                    st.rerun()
    
    # Sidebar with study guide
    with st.sidebar:
        st.markdown("## 📚 Study Guide")
        
        category_filter = st.selectbox(
            "Filter by category",
            ["All"] + sorted(list(set(m['category'] for m in METRICS_LIBRARY.values())))
        )
        
        st.markdown("---")
        
        for metric, data in sorted(METRICS_LIBRARY.items()):
            if category_filter == "All" or data['category'] == category_filter:
                with st.expander(f"📊 {metric}"):
                    st.markdown(f"**Category:** {data['category']}")
                    st.markdown(f"**Definition:** {data['definition']}")
                    st.markdown(f"**Good Range:** {data['good_range']}")
        
        st.markdown("---")
        if st.button("🔄 Reset Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.current_metric = None
            st.session_state.score = 0
            st.session_state.total_questions = 0
            st.session_state.show_answer = False
            st.session_state.used_metrics = []
            st.session_state.user_guess = ""
            st.rerun()