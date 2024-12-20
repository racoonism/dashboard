import os
import pandas as pd
import matplotlib.pyplot as plt

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script directory
os.chdir(script_dir)

# Filter files starting with a number and ending with ".csv"
# file_names = [filename for filename in os.listdir(script_dir) if filename.startswith(tuple("0123456789")) and filename.endswith(".csv")]
def required_capital(filename_trades, start_date, end_date, strats=None):

    file_names = [filename for filename in os.listdir(script_dir) if filename.endswith(filename_trades)]

    # Read the CSV files and store the trades in a list
    trades = []
    for file_name in file_names:
        df = pd.read_csv(file_name)
        trades.append(df)

    # Combine the trades from all strategies in chronological order
    combined_trades = pd.concat(trades)
    combined_trades['ExitTime'] = pd.to_datetime(combined_trades['ExitTime'])  # Convert ExitTime to datetime format
    combined_trades.sort_values('ExitTime', inplace=True)

     # Convert start_date and end_date to datetime data type
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    combined_trades = combined_trades[(combined_trades['ExitTime'] >= start_date) & (combined_trades['ExitTime'] <= end_date)]

    if not strats:
        strats = combined_trades["StrategyName"].unique()
        # [
        #     # '17 GoldLiquid_1minFix_original', 
        #         '23 StruckGold_edit',
        #     '10 TrendFollowerGoldcode', 
        #     '14 ESScalper_edit_NQ',
        #     '12 NQTrendFollower_original',
        #         '27 LSBEdipSpring',
        #     '18 RedSword_original', 
        #     '28 Tanker_edit', 
        #     '19 BlackGas_edit',
        #     '20 Watchmen_edit', 
        #     '29 WaveRider_original',
        #     '21 VioletScimitar_edit', 
        #     '31 FerrisWheel_original',
        #     '26 ClubBouncer_edit', 
        #     '13 ESScalper_edit',
        #     '24 CatalyticReverter_edit', 
        #     '15 BlueLightning_original_logging',
        #     '1 VariableTrend_original', 
        #     '22 LunchSnacker_edit', 
        #     '5 vwaptest',
        #     '25 TexasTea_edit', 
        #     '30 VWAPBouncer']

    combined_trades = combined_trades[combined_trades['StrategyName'].isin(strats)]

    # Calculate the cumulative profit and drawdown
    combined_trades['CumulativeProfit'] = combined_trades['Profit'].cumsum()
    combined_trades['Drawdown'] = combined_trades['CumulativeProfit'] - combined_trades['CumulativeProfit'].cummax()

    # Calculate the maximum drawdown
    max_drawdown = combined_trades['Drawdown'].min()

    # Calculate the Required Capital
    required_capital = abs(2 * max_drawdown) - combined_trades['CumulativeProfit'].min()

    # Plot the combined profit data series
    plt.figure(figsize=(12, 6))
    plt.plot(combined_trades['ExitTime'], combined_trades['CumulativeProfit'])
    plt.xlabel('Exit Time')
    plt.ylabel('Cumulative Profit')
    plt.title('Combined Profit Data Series')

    # Calculate the position for displaying text
    x_position = combined_trades['ExitTime'].iloc[-1]
    y_position = combined_trades['CumulativeProfit'].min()
    text = f"Net profit: {combined_trades['CumulativeProfit'].iloc[-1]:.2f} \
            \nMax Drawdown: {max_drawdown:.2f} \
            \nRequired Capital: {required_capital:.2f} \
            \nReturn to drawdown: {combined_trades['CumulativeProfit'].iloc[-1]/abs(max_drawdown):.2f}"
    
    # Display the maximum drawdown and required capital on the plot
    plt.text(x_position, y_position, text,
            ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.8))

    plt.savefig('RequiredCapital.png')
    plt.close()
