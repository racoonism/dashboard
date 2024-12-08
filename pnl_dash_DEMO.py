import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

# from azure_download import *
# fetch_file("Realtime_Log_DEMO.csv")
from dropbox_refresh_token import *
from dropbox_download_file import *

APP_KEY = st.secrets["APP_KEY"] or os.getenv("APP_KEY")
APP_SECRET = st.secrets["APP_SECRET"] or os.getenv("APP_SECRET")
REFRESH_TOKEN = st.secrets["DROPBOX_REFRESH_TOKEN"] or os.getenv("DROPBOX_REFRESH_TOKEN")
ACCESS_TOKEN = get_access_token(APP_KEY, APP_SECRET, REFRESH_TOKEN)

### DOWNLOAD AND READ 
# download_from_dropbox("/Realtime_Log_SIM.csv", "Realtime_Log_SIM.csv", ACCESS_TOKEN)
# Load the data
@st.cache_data
def load_data():
    # Load your data here
    return pd.read_csv('Realtime_Log_DEMO.csv')
# df = load_data

### READ CONTENT DIRECTLY WITHOUT DOWNLOAD
df = download_from_dropbox_IO("/Realtime_Log_DEMO.csv", ACCESS_TOKEN)

# Calculate the first day of the current month
today = date.today()
first_day_of_month = today.replace(day=1)

# Sidebar - Date range selection and strategy selection
start_date = st.sidebar.date_input("Start date", value=first_day_of_month)
end_date = st.sidebar.date_input("End date")

# Sidebar with "Select All" option
all_strategies = df['StrategyName'].unique().tolist()
all_strategies_option = ["Select All"] + all_strategies  # Add "Select All" option

# Multiselect widget
selected_strategies = st.sidebar.multiselect(
    "Select strategies",
    all_strategies_option,
    default="Select All"
)

# Handle "Select All" logic
if "Select All" in selected_strategies:
    selected_strategies = all_strategies  


# Convert 'ExitTime' column to datetime
df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.normalize()
print(df.head())

# Exclude economic events
economic_events = ['2024-05-01']

# Convert economic_events to datetime objects
economic_events = pd.to_datetime(economic_events)
print(economic_events)

# Filter out rows where 'ExitTime' matches any of the economic_events
filtered_df = df.loc[~df['ExitTime'].isin(economic_events.date)]
print("filtered 1")
print(filtered_df)

# Filter data
filtered_df = filtered_df[filtered_df['StrategyName'].isin(selected_strategies)]

filtered_df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.date
print(start_date)
filtered_df = filtered_df[(filtered_df['ExitTime'] >= start_date) & (filtered_df['ExitTime'] <= end_date)]
print(filtered_df)

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


