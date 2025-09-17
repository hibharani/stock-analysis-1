import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class StockAnalyzer:
    def __init__(self):
        self.scoring_weights = {
            'pe_score': 0.25,
            'volume_score': 0.20,
            'momentum_score': 0.25,
            'profit_score': 0.30
        }

    def calculate_pe_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate PE ratio score (lower is better)
        Score: 10 for PE < 15, 8 for PE 15-25, 5 for PE 25-35, 2 for PE > 35
        """
        pe_scores = []
        for pe in df['pe_ratio']:
            if pe <= 0 or pd.isna(pe):
                pe_scores.append(1)  # Penalty for missing/invalid PE
            elif pe < 15:
                pe_scores.append(10)
            elif pe < 25:
                pe_scores.append(8)
            elif pe < 35:
                pe_scores.append(5)
            else:
                pe_scores.append(2)
        return pd.Series(pe_scores)

    def calculate_volume_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate volume score based on relative volume
        Higher volume gets higher score
        """
        if df['volume'].sum() == 0:
            return pd.Series([5] * len(df))

        volume_percentiles = df['volume'].rank(pct=True)
        volume_scores = []

        for percentile in volume_percentiles:
            if percentile >= 0.8:
                volume_scores.append(10)
            elif percentile >= 0.6:
                volume_scores.append(8)
            elif percentile >= 0.4:
                volume_scores.append(6)
            elif percentile >= 0.2:
                volume_scores.append(4)
            else:
                volume_scores.append(2)

        return pd.Series(volume_scores)

    def calculate_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate momentum score based on 30-day price change
        Positive momentum gets higher score
        """
        momentum_scores = []
        for momentum in df['momentum_30d']:
            if pd.isna(momentum):
                momentum_scores.append(5)
            elif momentum > 20:
                momentum_scores.append(10)
            elif momentum > 10:
                momentum_scores.append(8)
            elif momentum > 0:
                momentum_scores.append(6)
            elif momentum > -10:
                momentum_scores.append(4)
            else:
                momentum_scores.append(2)
        return pd.Series(momentum_scores)

    def calculate_profit_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate profitability score based on profit margin and ROE
        """
        profit_scores = []

        for idx, row in df.iterrows():
            profit_margin = row.get('profit_margin', 0)
            roe = row.get('roe', 0)

            # Handle missing values
            if pd.isna(profit_margin):
                profit_margin = 0
            if pd.isna(roe):
                roe = 0

            # Convert to percentage if needed
            if profit_margin < 1:
                profit_margin *= 100
            if roe < 1:
                roe *= 100

            # Combined score based on both metrics
            score = 0

            # Profit margin scoring
            if profit_margin > 20:
                score += 5
            elif profit_margin > 10:
                score += 4
            elif profit_margin > 5:
                score += 3
            elif profit_margin > 0:
                score += 2
            else:
                score += 1

            # ROE scoring
            if roe > 20:
                score += 5
            elif roe > 15:
                score += 4
            elif roe > 10:
                score += 3
            elif roe > 5:
                score += 2
            else:
                score += 1

            profit_scores.append(score)

        return pd.Series(profit_scores)

    def calculate_overall_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate overall investment score for each stock
        """
        # Calculate individual scores
        df['pe_score'] = self.calculate_pe_score(df)
        df['volume_score'] = self.calculate_volume_score(df)
        df['momentum_score'] = self.calculate_momentum_score(df)
        df['profit_score'] = self.calculate_profit_score(df)

        # Calculate weighted overall score
        df['overall_score'] = (
            df['pe_score'] * self.scoring_weights['pe_score'] +
            df['volume_score'] * self.scoring_weights['volume_score'] +
            df['momentum_score'] * self.scoring_weights['momentum_score'] +
            df['profit_score'] * self.scoring_weights['profit_score']
        ).round(2)

        return df

    def get_top_stocks(self, df: pd.DataFrame, metric: str = 'overall_score', top_n: int = 10) -> pd.DataFrame:
        """
        Get top N stocks based on specified metric
        """
        if metric not in df.columns:
            raise ValueError(f"Metric '{metric}' not found in dataframe")

        return df.nlargest(top_n, metric)

    def get_stocks_by_criteria(self, df: pd.DataFrame, criteria: Dict) -> pd.DataFrame:
        """
        Filter stocks based on specific criteria

        criteria example:
        {
            'min_pe': 0,
            'max_pe': 25,
            'min_momentum': 0,
            'min_profit_margin': 5
        }
        """
        filtered_df = df.copy()

        if 'min_pe' in criteria:
            filtered_df = filtered_df[filtered_df['pe_ratio'] >= criteria['min_pe']]
        if 'max_pe' in criteria:
            filtered_df = filtered_df[filtered_df['pe_ratio'] <= criteria['max_pe']]
        if 'min_momentum' in criteria:
            filtered_df = filtered_df[filtered_df['momentum_30d'] >= criteria['min_momentum']]
        if 'min_profit_margin' in criteria:
            profit_margin_pct = filtered_df['profit_margin'] * 100
            filtered_df = filtered_df[profit_margin_pct >= criteria['min_profit_margin']]
        if 'min_volume' in criteria:
            filtered_df = filtered_df[filtered_df['volume'] >= criteria['min_volume']]

        return filtered_df

    def get_sector_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze stocks by sector
        """
        sector_analysis = df.groupby('sector').agg({
            'overall_score': ['mean', 'count'],
            'pe_ratio': 'mean',
            'momentum_30d': 'mean',
            'profit_margin': 'mean'
        }).round(2)

        sector_analysis.columns = ['avg_score', 'stock_count', 'avg_pe', 'avg_momentum', 'avg_profit_margin']
        return sector_analysis.sort_values('avg_score', ascending=False)