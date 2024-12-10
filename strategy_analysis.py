import pandas as pd
from itertools import combinations

def get_top_strategies_by_daytype(
    df, start_date, end_date, number_of_strats, ignore_daytype=True, strategies_to_ignore=None
):
    '''
    Get the top N combinations of strategies based on profit and day type.

    Parameters:
    - df: DataFrame containing strategy data.
    - start_date: Start date for filtering data (string in 'YYYY-MM-DD' format).
    - end_date: End date for filtering data (string in 'YYYY-MM-DD' format).
    - number_of_strats: Number of strategies to combine and evaluate.
    - ignore_daytype: Whether to ignore the day type when evaluating combinations.
    - strategies_to_ignore: List of strategies to exclude from analysis.

    Returns:
    - top_3_strategies_by_daytype: DataFrame of top 3 strategy combinations by day type.
    '''
    if ignore_daytype:
        df['DayType'] = 'Unclassified day'

    # Convert dates to datetime
    df['ExitTime'] = pd.to_datetime(df['ExitTime'])
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Filter data based on date range
    filtered_df = df[(df['ExitTime'] >= start_date) & (df['ExitTime'] <= end_date)]

    # Exclude specified strategies
    if strategies_to_ignore:
        filtered_df = filtered_df[~filtered_df['StrategyName'].isin(strategies_to_ignore)]

    # Group data by day type and strategy combinations
    top_3_strategies_by_daytype = {}
    for day_type, group in filtered_df.groupby(['DayType']):
        strategy_profits = {}
        strategies = group['StrategyName'].unique()

        # Evaluate combinations of strategies
        for combination in combinations(strategies, number_of_strats):
            combined_profit = group[group['StrategyName'].isin(combination)]['Profit'].sum()
            strategy_profits[combination] = combined_profit

        # Sort and get top 3 combinations
        sorted_combinations = sorted(strategy_profits.items(), key=lambda x: x[1], reverse=True)
        top_3_strategies_by_daytype[day_type] = sorted_combinations[:3]

    return top_3_strategies_by_daytype

