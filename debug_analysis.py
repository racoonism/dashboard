from dropbox_refresh_token import *
from dropbox_download_file import *
from strategy_analysis import *

# Load data from Dropbox
APP_KEY = st.secrets["APP_KEY"] or os.getenv("APP_KEY")
APP_SECRET = st.secrets["APP_SECRET"] or os.getenv("APP_SECRET")
REFRESH_TOKEN = st.secrets["DROPBOX_REFRESH_TOKEN"] or os.getenv("DROPBOX_REFRESH_TOKEN")
ACCESS_TOKEN = get_access_token(APP_KEY, APP_SECRET, REFRESH_TOKEN)

df = download_from_dropbox_IO("/Realtime_Log_SIM.csv", ACCESS_TOKEN)

start_date = '01-01-2022'
end_date = '22-12-2024'
number_of_strats = 3
ignore_daytype = True
strategies_to_ignore = ['1 VariableTrend_original', '14 ESScalper_edit_NQ']


results = get_top_strategies_by_daytype(
            df=df,
            start_date=start_date,
            end_date=end_date,
            number_of_strats=number_of_strats,
            ignore_daytype=ignore_daytype,
            strategies_to_ignore=strategies_to_ignore
        )

