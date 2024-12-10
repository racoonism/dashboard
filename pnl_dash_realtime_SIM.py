import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date
from strategy_analysis import get_top_strategies_by_daytype
from dropbox_refresh_token import *
from dropbox_download_file import *

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

df = download_from_dropbox_IO("/Realtime_Log_SIM.csv", ACCESS_TOKEN)

# Sidebar inputs for filtering data
st.sidebar.header("Filter Options")
start_date = st.sidebar.date_input("Start date", value=date.today().replace(day=1))  # First day of current month
end_date = st.sidebar.date_input("End date", value=date.today())
selected_strategies = st.sidebar.multiselect("Select strategies", df['StrategyName'].unique())

# Convert 'ExitTime' column to datetime
df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.date

# Filter data based on user input
filtered_df = df[df['StrategyName'].isin(selected_strategies)]
filtered_df = filtered_df[(filtered_df['ExitTime'] >= start_date) & (filtered_df['ExitTime'] <= end_date)]

# Group data by date and StrategyName and calculate sum of profit
grouped_df = filtered_df.groupby(['ExitTime', 'StrategyName']).agg({'Profit': 'sum'}).reset_index()
grouped_df['CumulativeProfit'] = grouped_df.groupby('StrategyName')['Profit'].cumsum()

# Calculate combined cumulative profit
combined_cumulative_profit = filtered_df.groupby('ExitTime')['Profit'].sum().reset_index()
combined_cumulative_profit['CumulativeProfit'] = combined_cumulative_profit['Profit'].cumsum()
combined_cumulative_profit['StrategyName'] = 'All Strategies'

# Append combined cumulative profit to daily profit dataframe
daily_profit = pd.concat([grouped_df, combined_cumulative_profit], ignore_index=True)

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
            st.write(f"### Top 3 strategy combinations: {day_type_label}")
            for rank, (combination, profit) in enumerate(top_combinations, start=1):
                st.write(f"**Rank {rank}:** {list(combination)} with profit {profit}")

    except Exception as e:
        st.error(f"Error during analysis: {e}")

# Display the loaded data
st.write("Loaded Data:")
st.dataframe(df)
