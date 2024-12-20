import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.font_manager import FontProperties

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script directory
os.chdir(script_dir)

def correlation(filename_trades, start_date="2008-01-01", end_date="2075-12-31", strats=None):
    # Filter files starting with a number and ending with ".csv"
    # file_names = [filename for filename in os.listdir(script_dir) if filename.startswith(tuple("0123456789")) and filename.endswith(".csv")]
    file_names = [filename for filename in os.listdir(script_dir) if filename.endswith(filename_trades)]

    # Read the CSV files and store the trades in a list
    trades = []
    strategies = []
    for file_name in file_names:
        file_path = os.path.join(script_dir, file_name)  # Get the full file path
        df = pd.read_csv(file_path)
        trades.append(df)
        strategy_name = df['StrategyName'].iloc[0]  # Get the strategy name from the first row
        strategies.append(strategy_name)

    # Combine the trades from all strategies in a single DataFrame
    combined_trades = pd.concat(trades)

    if not strats:
        strats = ["1 VariableTrend_original", "12 NQTrendFollower_original", "13 ESScalper_edit",
                  "14 ESScalper_edit_NQ", "26 ClubBouncer_edit", "5 vwaptest", "24 CatalyticReverter_edit", 
                  "19 BlackGas_edit", "MiniCatch2"]
        corr_title = 'Correlation Matrix - DEFAULT portfolio - select strategies for custom portfolio'
    else:
        strats = strats
        corr_title = 'Correlation Matrix'

    combined_trades = combined_trades[combined_trades['StrategyName'].isin(strats)]

    # Aggregate profits by day
    combined_trades['ExitTime'] = pd.to_datetime(combined_trades['ExitTime'])#, format='%m/%d/%Y %I:%M:%S')  # Convert ExitTime to datetime format
    combined_trades['Profit'] = pd.to_numeric(combined_trades['Profit'])  # Convert Profit to numeric type
    combined_trades['Date'] = combined_trades['ExitTime'].dt.date
    daily_profits = combined_trades.groupby(['StrategyName', 'Date'])['Profit'].sum().reset_index()


    # Convert the 'Date' column in the daily_profits DataFrame to datetime data type
    daily_profits['Date'] = pd.to_datetime(daily_profits['Date'])

    # Convert start_date and end_date to datetime data type
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter daily_profits based on start_date and end_date
    daily_profits = daily_profits[(daily_profits['Date'] >= start_date) & (daily_profits['Date'] <= end_date)]
    
    # Pivot the data to create a correlation matrix
    pivot_table = daily_profits.pivot(index='Date', columns='StrategyName', values='Profit')


    # Calculate the correlation matrix
    correlation_matrix = pivot_table.corr()

    # # Mask the diagonal correlation values
    # correlation_matrix = correlation_matrix.where(~np.eye(correlation_matrix.shape[0], dtype=bool), 0)

    # Mask the diagonal correlation values and values above 0.5
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=0)
    correlation_matrix = correlation_matrix.mask(mask)
    # correlation_matrix = correlation_matrix.mask(correlation_matrix <= 0.5)

    # Plot the correlation matrix as a heatmap and save as image
    plt.figure(figsize=(12, 10))
    # mask = correlation_matrix <= 0.5
    annot_mask = correlation_matrix >= 0.5
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    # sns.heatmap(correlation_matrix, cmap='RdYlGn_r', annot=True, fmt='.2f', vmin=-1, vmax=1, mask=correlation_matrix <= 0.5)
    sns.heatmap(correlation_matrix, cmap=cmap, annot=True, fmt='.2f', annot_kws={"weight": "bold", "color": "black", "fontsize": 12}, cbar=False)
    plt.title(corr_title)
    plt.savefig('correlation_matrix.png')
    plt.close()

    # # Plot the cumulative profit of each strategy and save as image
    # plt.figure(figsize=(12, 6))
    # num_strategies = len(strategies)
    # starting_amount = num_strategies * 1000
    # for strategy in strategies:
    #     strategy_data = daily_profits[daily_profits['StrategyName'] == strategy]
    #     cumulative_profit = strategy_data.groupby('Date')['Profit'].sum().cumsum()
    #     plt.plot(strategy_data['Date'], cumulative_profit + starting_amount, label=strategy)

    # # Plot the cumulative profit of all strategies
    # total_profit = daily_profits.groupby('Date')['Profit'].sum().cumsum()
    # plt.plot(total_profit.index, total_profit + starting_amount, label='Total Profit',  linewidth=2.5, color ='Red')

    # plt.xlabel('Date')
    # plt.ylabel('Cumulative Profit')
    # plt.title('Cumulative Profit of Strategies')
    # plt.legend()
    # plt.savefig('cumulative_profit.png')
    # plt.close()

# correlation('AllTrades_Log')