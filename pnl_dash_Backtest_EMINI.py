import streamlit as st
import pandas as pd
import altair as alt
from RequiredCapital import required_capital
from Correlation import correlation
from datetime import datetime, timedelta
from dropbox_refresh_token import *
from dropbox_download_file import *
from strategy_analysis import get_top_strategies_by_daytype

# Load data from Dropbox
APP_KEY = st.secrets["APP_KEY"] or os.getenv("APP_KEY")
APP_SECRET = st.secrets["APP_SECRET"] or os.getenv("APP_SECRET")
REFRESH_TOKEN = st.secrets["DROPBOX_REFRESH_TOKEN"] or os.getenv("DROPBOX_REFRESH_TOKEN")
ACCESS_TOKEN = get_access_token(APP_KEY, APP_SECRET, REFRESH_TOKEN)

@st.cache_data
def download_from_dropbox_IO(dropbox_path, access_token):
    import dropbox
    import io

    dbx = dropbox.Dropbox(access_token)
    _, res = dbx.files_download(dropbox_path)
    return pd.read_csv(io.BytesIO(res.content))

df = download_from_dropbox_IO("/AllTrades_Log_EMINI.csv", ACCESS_TOKEN)

df_original = df

# Sidebar - Date range selection and strategy selection
# Get today's date
today = datetime.today()
# Calculate the start date as one year ago from today
start_date = today - timedelta(days=365)
# Allow the user to select a custom start date
start_date = st.sidebar.date_input("Start date", start_date)
end_date = st.sidebar.date_input("End date")

# selected_strategies = st.sidebar.multiselect("Select strategies", df['StrategyName'].unique())
selected_strategies = st.multiselect('Select a portfolio of strategies to calculate net profit', df_original['StrategyName'].unique())
exclude_econ_events = st.sidebar.checkbox("Exclude economic events")

# Convert 'ExitTime' column to datetime
df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.normalize()
print(df.head())

# Exclude economic events
economic_events = download_from_dropbox_IO("/US_events_high.csv", ACCESS_TOKEN)
economic_events = economic_events["date"]
# print(economic_events)

# Convert economic_events to datetime objects
economic_events = pd.to_datetime(economic_events, format="%d/%m/%Y")
# print(economic_events)

if exclude_econ_events:
    # Filter out rows where 'ExitTime' matches any of the economic_events
    filtered_df = df.loc[~df['ExitTime'].isin(economic_events.dt.date)]
    print("filtered 1")
    print(filtered_df)
else:
    filtered_df = df


#  Multi-select date picker widget for selecting dates to exclude
excluded_dates = st.sidebar.multiselect('Select dates to exclude', pd.date_range(start='2008-01-01', end='2025-12-31').date)
filtered_df = filtered_df.loc[~filtered_df['ExitTime'].isin(excluded_dates)]

# Filter data
filtered_df = filtered_df[filtered_df['StrategyName'].isin(selected_strategies)]

filtered_df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.date
# print(start_date)
filtered_df = filtered_df[(filtered_df['ExitTime'] >= start_date) & (filtered_df['ExitTime'] <= end_date)]
# print(filtered_df)

# Group by date and StrategyName and calculate sum of profit
grouped_df = filtered_df.groupby(['ExitTime', 'StrategyName']).agg({'Profit': 'sum'}).reset_index()

# Calculate cumulative profit for each day and each strategy
grouped_df['CumulativeProfit'] = grouped_df.groupby('StrategyName')['Profit'].cumsum()
print(grouped_df)
print(filtered_df)

# Calculate combined cumulative profit
combined_cumulative_profit = filtered_df.groupby('ExitTime')['Profit'].sum().reset_index()
combined_cumulative_profit['CumulativeProfit'] = combined_cumulative_profit['Profit'].cumsum()
combined_cumulative_profit['StrategyName'] = 'All Strategies'
print(combined_cumulative_profit)

# Append combined cumulative profit to daily profit dataframe
daily_profit = pd.concat([grouped_df, combined_cumulative_profit], ignore_index=True)
print(daily_profit)

### STRATCOMBO START
# Add new feature: Top strategy combinations
st.sidebar.header("Top 3 strategy combinations")
number_of_strats = st.sidebar.slider("Number of strategies to combine", min_value=1, max_value=10, value=4)
ignore_daytype = st.sidebar.checkbox("Ignore day type", value=True)
strategies = df['StrategyName'].unique().tolist()
strategies_to_ignore = st.sidebar.multiselect("Select strategies to ignore", strategies)

if st.sidebar.button("### Find Top 3 strategy combinations"):
    # st.write("Running strategy analysis...")
    try:
        # Run the analysis
        results = get_top_strategies_by_daytype(
            df=df,
            start_date=start_date,
            end_date=end_date,
            number_of_strats=number_of_strats,
            ignore_daytype=ignore_daytype,
            strategies_to_ignore=strategies_to_ignore
        )

        # Display the results
        for day_type, top_combinations in results.items():
            day_type_label = "All" if day_type is None else day_type
            st.write(f"### Top 3 strategy combinations:") #{day_type_label}")
            for rank, (combination, profit) in enumerate(top_combinations, start=1):
                st.markdown(f"**{rank} - Profit: {round(profit,)}:**  \n{list(combination)}")
                # st.write(f"**{rank} - Profit: {profit}:**\n: {list(combination)}")

    except Exception as e:
        st.error(f"Error during analysis: {e}")
### STRATCOMBO END

# Plot cumulative profit for each strategy and all strategies combined
chart = alt.Chart(daily_profit).mark_line().encode(
    x='ExitTime:T',
    y='CumulativeProfit:Q',
    color='StrategyName:N',
    tooltip=['StrategyName', 'ExitTime', 'CumulativeProfit']
).properties(
    width=800,
    height=400
).interactive()

st.altair_chart(chart, use_container_width=True)


selected_strategies = st.multiselect('Select a portfolio of strategies to calculate required capital', df_original['StrategyName'].unique())

# Call the required_capital function with selected strategies
required_capital('AllTrades_Log', start_date, end_date, selected_strategies)
correlation('AllTrades_Log', start_date, end_date, selected_strategies)

# Display the generated plot
st.image('RequiredCapital.png', caption='Combined Profit Data Series')
st.image('correlation_matrix.png', caption='Correlation matrix of all strats')

