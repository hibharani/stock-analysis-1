import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from stock_data import IndianStockDataFetcher
from stock_analyzer import StockAnalyzer

# Page config
st.set_page_config(
    page_title="Indian Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# Initialize classes
@st.cache_data
def get_stock_fetcher():
    return IndianStockDataFetcher()

@st.cache_data
def get_analyzer():
    return StockAnalyzer()

def load_stock_data():
    """Load stock data with caching"""
    fetcher = get_stock_fetcher()
    analyzer = get_analyzer()

    with st.spinner("Fetching Nifty 50 stock data... This may take a few minutes."):
        # Get Nifty 50 symbols
        stock_list = fetcher.get_nse_stocks()
        symbols = [stock['symbol'] for stock in stock_list]

        # Fetch detailed data
        df = fetcher.get_multiple_stocks_data(symbols, max_stocks=20)

        if not df.empty:
            # Analyze stocks
            analyzed_df = analyzer.calculate_overall_score(df)
            return analyzed_df
        else:
            return pd.DataFrame()

def main():
    st.title("🇮🇳 Indian Stock Analyzer")
    st.markdown("Find the best Indian stocks based on PE ratio, volume, momentum, and profitability")

    # Sidebar
    st.sidebar.header("📊 Analysis Options")

    # Load data button
    if st.sidebar.button("🔄 Load Fresh Data", type="primary"):
        st.session_state.stock_data = None
        st.session_state.analyzed_data = None
        st.cache_data.clear()

    # Load data if not already loaded
    if st.session_state.analyzed_data is None:
        st.session_state.analyzed_data = load_stock_data()

    df = st.session_state.analyzed_data

    if df is None or df.empty:
        st.error("❌ No stock data available. Please try loading fresh data.")
        return

    # Sidebar filters
    st.sidebar.subheader("🔍 Filters")

    # PE ratio filter
    pe_range = st.sidebar.slider(
        "PE Ratio Range",
        min_value=0.0,
        max_value=float(df['pe_ratio'].max()) if df['pe_ratio'].max() > 0 else 100.0,
        value=(0.0, 50.0),
        step=1.0
    )

    # Momentum filter
    momentum_min = st.sidebar.number_input(
        "Minimum 30-day Momentum (%)",
        value=-50.0,
        step=1.0
    )

    # Volume filter
    volume_min = st.sidebar.number_input(
        "Minimum Volume",
        value=0,
        step=1000
    )

    # Apply filters
    filtered_df = df[
        (df['pe_ratio'] >= pe_range[0]) &
        (df['pe_ratio'] <= pe_range[1]) &
        (df['momentum_30d'] >= momentum_min) &
        (df['volume'] >= volume_min)
    ]

    # Main content
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📈 Total Stocks", len(filtered_df))
    with col2:
        st.metric("💰 Avg Market Cap", f"₹{filtered_df['marketCap'].mean()/10000000:.1f}Cr")
    with col3:
        st.metric("📊 Avg PE Ratio", f"{filtered_df['pe_ratio'].mean():.1f}")
    with col4:
        st.metric("🚀 Avg Momentum", f"{filtered_df['momentum_30d'].mean():.1f}%")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top Recommendations", "📊 Detailed Analysis", "🎯 Sector Analysis", "📈 Charts"])

    with tab1:
        st.subheader("🏆 Top Stock Recommendations")

        # Top stocks by overall score
        top_stocks = filtered_df.nlargest(10, 'overall_score')

        if not top_stocks.empty:
            for idx, stock in top_stocks.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

                    with col1:
                        st.markdown(f"**{stock['symbol']}**")
                        st.caption(stock['companyName'][:30] + "...")

                    with col2:
                        st.metric("Score", f"{stock['overall_score']:.1f}/10")

                    with col3:
                        st.metric("Price", f"₹{stock['currentPrice']:.1f}")

                    with col4:
                        st.metric("PE", f"{stock['pe_ratio']:.1f}")

                    with col5:
                        momentum_color = "normal" if stock['momentum_30d'] >= 0 else "inverse"
                        st.metric("Momentum", f"{stock['momentum_30d']:.1f}%", delta=None)

                    st.divider()
        else:
            st.info("No stocks match the current filters.")

    with tab2:
        st.subheader("📊 Detailed Stock Analysis")

        # Display options
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                ["overall_score", "pe_ratio", "momentum_30d", "volume", "currentPrice"]
            )
        with col2:
            ascending = st.checkbox("Ascending order", value=False)

        # Display filtered data
        display_df = filtered_df.sort_values(sort_by, ascending=ascending)

        # Select columns to display
        columns_to_show = [
            'symbol', 'companyName', 'currentPrice', 'pe_ratio',
            'momentum_30d', 'volume', 'overall_score', 'sector'
        ]

        st.dataframe(
            display_df[columns_to_show],
            use_container_width=True,
            height=400
        )

    with tab3:
        st.subheader("🎯 Sector-wise Analysis")

        analyzer = get_analyzer()
        sector_analysis = analyzer.get_sector_analysis(filtered_df)

        if not sector_analysis.empty:
            st.dataframe(sector_analysis, use_container_width=True)

            # Sector performance chart
            fig = px.bar(
                sector_analysis.reset_index(),
                x='sector',
                y='avg_score',
                title="Average Score by Sector",
                color='avg_score',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sector data available.")

    with tab4:
        st.subheader("📈 Stock Analysis Charts")

        if len(filtered_df) > 0:
            # PE vs Momentum scatter plot
            fig1 = px.scatter(
                filtered_df,
                x='pe_ratio',
                y='momentum_30d',
                size='volume',
                color='overall_score',
                hover_data=['symbol', 'currentPrice'],
                title="PE Ratio vs Momentum (Size = Volume, Color = Overall Score)",
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Score distribution
            fig2 = px.histogram(
                filtered_df,
                x='overall_score',
                title="Distribution of Overall Scores",
                nbins=20
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data to display charts.")

if __name__ == "__main__":
    main()