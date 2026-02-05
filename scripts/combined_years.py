import argparse
import pandas as pd
from compute_averages import monthly_average, daily_average
import os


parser = argparse.ArgumentParser()
parser.add_argument("--input", nargs="+", required=True)
parser.add_argument("--all_data", required=True)
parser.add_argument("--monthly", required=True)
parser.add_argument("--daily", required=True)
args = parser.parse_args()


new_dataframes = [pd.read_csv(f) for f in args.input]
new_df = pd.concat(new_dataframes, ignore_index=True)


if os.path.exists(args.all_data):
    existing_df = pd.read_csv(args.all_data)
    new_years = set(new_df['year']) - set(existing_df['year'])
    if new_years:
        to_append = new_df[new_df['year'].isin(new_years)]
        df_all = pd.concat([existing_df, to_append], ignore_index=True)
    else:
        df_all = existing_df
else:
    df_all = new_df

df_all.to_csv(args.all_data, index=False)


monthly_df = pd.read_csv(args.monthly) if os.path.exists(args.monthly) else pd.DataFrame()
new_monthly = monthly_average(new_df)

if not monthly_df.empty:
    combined_monthly = pd.concat([monthly_df, new_monthly], ignore_index=True)
else:
    combined_monthly = new_monthly

combined_monthly.to_csv(args.monthly, index=False)


daily_df = pd.read_csv(args.daily) if os.path.exists(args.daily) else pd.DataFrame()
new_daily = daily_average(new_df)

if not daily_df.empty:
    combined_daily = pd.concat([daily_df, new_daily], ignore_index=True)
else:
    combined_daily = new_daily

combined_daily.to_csv(args.daily, index=False)
