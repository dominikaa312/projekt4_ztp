import argparse
import pandas as pd
from compute_averages import monthly_average, daily_average
import os


parser = argparse.ArgumentParser()
parser.add_argument("--input", nargs="+", required=True)
args = parser.parse_args()

scripts_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(scripts_dir)
all_data_out_path = os.path.join(base_dir, "data", "all_data.csv")

dataframes = [pd.read_csv(df) for df in args.input]
df_all_data = pd.concat(dataframes, ignore_index=True)
df_all_data.to_csv(all_data_out_path, index=False)

monthly_df = monthly_average(df_all_data)

daily_df = daily_average(df_all_data)

