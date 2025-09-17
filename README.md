# Indian Stock Analyzer 📈

A Streamlit web application for analyzing Indian stocks from the NSE market. Find the best stocks based on PE ratio, volume, momentum, and profitability metrics.

## Features

- 🔍 **Real-time Data**: Fetches live data for Nifty 50 stocks using Yahoo Finance
- 📊 **Multi-factor Analysis**: Analyzes stocks based on:
  - PE Ratio (Price-to-Earnings)
  - Trading Volume
  - 30-day Price Momentum
  - Profitability Metrics (ROE, Profit Margin)
- 🏆 **Smart Scoring**: Weighted scoring system to rank stocks
- 🎯 **Sector Analysis**: Compare performance across different sectors
- 📈 **Interactive Charts**: Visualize stock relationships and distributions
- 🔧 **Flexible Filters**: Customize analysis based on your criteria

## Live Demo

[Deploy on Streamlit Cloud](https://share.streamlit.io/)

## Local Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd stock-analysis-1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Load Data**: Click "Load Fresh Data" to fetch current stock information
2. **Apply Filters**: Use the sidebar to filter stocks by PE ratio, momentum, and volume
3. **View Recommendations**: Check the "Top Recommendations" tab for best-scoring stocks
4. **Analyze Details**: Explore detailed metrics in the "Detailed Analysis" tab
5. **Sector Insights**: Compare sector performance in the "Sector Analysis" tab
6. **Visualize Data**: View interactive charts in the "Charts" tab

## Scoring Methodology

The application uses a weighted scoring system:

- **PE Score (25%)**: Lower PE ratios score higher
- **Volume Score (20%)**: Higher trading volumes score higher
- **Momentum Score (25%)**: Positive price momentum scores higher
- **Profit Score (30%)**: Higher profit margins and ROE score higher

## Deployment on Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select your repository
5. Deploy with one click!

## Data Sources

- **Stock Data**: Yahoo Finance API via yfinance library
- **Market Coverage**: NSE (National Stock Exchange) Nifty 50 stocks
- **Update Frequency**: Real-time data fetching on demand

## Disclaimer

This application is for educational and informational purposes only. It should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions.

## License

MIT License