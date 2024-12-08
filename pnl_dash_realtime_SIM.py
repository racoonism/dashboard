import streamlit as st
import pandas as pd
import altair as alt
# from azure_download import *
# fetch_file("Realtime_Log_SIM.csv")

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
    return pd.read_csv('Realtime_Log_SIM.csv')
# df = load_data

### READ CONTENT DIRECTLY WITHOUT DOWNLOAD
df = download_from_dropbox_IO("/Realtime_Log_SIM.csv", ACCESS_TOKEN)


# Sidebar - Date range selection and strategy selection
start_date = st.sidebar.date_input("Start date")
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
df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.date

# Filter data
filtered_df = df[df['StrategyName'].isin(selected_strategies)]
filtered_df = filtered_df[(filtered_df['ExitTime'] >= start_date) & (filtered_df['ExitTime'] <= end_date)]
# Detect environment
is_production = os.getenv("STREAMLIT_ENV") == "production"

# Conditionally save CSV for local debugging
if not is_production:
    debug_csv_path = "realtime_log_SIM_short_streamlit.csv"
    filtered_df.to_csv(debug_csv_path, index=False)
    print(f"Debugging CSV saved: {debug_csv_path}")
else:
    print("Running in production, no CSV saved.")

# Add a checkbox for debugging
# if st.checkbox("Save CSV for debugging"):
#     filtered_df.to_csv("realtime_log_SIM_short_streamlit.csv", index=False)
#     st.write("CSV saved for debugging!")

# Group by date and StrategyName and calculate sum of profit
grouped_df = filtered_df.groupby(['ExitTime', 'StrategyName']).agg({'Profit': 'sum'}).reset_index()

# Calculate cumulative profit for each day and each strategy
grouped_df['CumulativeProfit'] = grouped_df.groupby('StrategyName')['Profit'].cumsum()
# print(grouped_df)
# print(filtered_df)

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

# Display the dataframes in the Streamlit app
st.write("Combined Cumulative Profit:")
st.dataframe(combined_cumulative_profit)

st.write("Daily Profit and Loss Data:")
st.dataframe(daily_profit)

st.write("Full Daily Profit and Loss Data:")
st.dataframe(filtered_df)

# Sort data by ExitTime to ensure the earliest exit times come first
filtered_df_sorted = filtered_df.sort_values(by=['ExitTime', 'StrategyName', 'ExitTime'])

# Group by ExitTime and StrategyName, then take the first profit entry based on the earliest exit time
first_profit_per_day = filtered_df_sorted.groupby(['ExitTime', 'StrategyName']).first().reset_index()

# Calculate cumulative profit for each day and each strategy based on the first entry
first_profit_per_day['CumulativeProfit'] = first_profit_per_day.groupby('StrategyName')['Profit'].cumsum()

# Display the first profit/loss per strategy per day in the Streamlit app
st.write("First Profit/Loss per Strategy per Day:")
st.dataframe(first_profit_per_day)

# Calculate combined cumulative profit for all strategies based on the first entry per day
combined_first_profit = first_profit_per_day.groupby('ExitTime')['Profit'].sum().reset_index()
combined_first_profit['CumulativeProfit'] = combined_first_profit['Profit'].cumsum()
combined_first_profit['StrategyName'] = 'All Strategies'

# Display the combined cumulative profit for all strategies
st.write("Combined First Profit/Loss for All Strategies per Day:")
st.dataframe(combined_first_profit)