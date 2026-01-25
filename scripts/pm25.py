from compute_averages import *
from visualizations import *
import pandas as pd
import os
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--threshold", type=float, required=True)
parser.add_argument("--cities", nargs="+", required=True)
args = parser.parse_args()

year = args.year
threshold = args.threshold
cities = args.cities


scripts_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(scripts_dir)


data_path = os.path.join(base_dir, "data", "all_data.csv")
monthly_avg_path = os.path.join(base_dir, "data", "monthly_average.csv")

exceedance_out_path = os.path.join("results", "pm25", str(year), "exceedance_days.csv")
os.makedirs(os.path.dirname(exceedance_out_path), exist_ok=True)

monthly_out_path = os.path.join("results", "pm25", str(year), "monthly_data.csv")

heatmap_out_path = os.path.join("results", "pm25", str(year), "figures", "heatmap.png")
os.makedirs(os.path.dirname(heatmap_out_path), exist_ok=True)
plot_trends_out_path = os.path.join("results", "pm25", str(year), "figures", "plot_city_trends.png")


data = pd.read_csv(data_path)
monthly_avg = pd.read_csv(monthly_avg_path)


exceedance_days = count_days_over_threshold(data, threshold, year, cities)
monthly_df = monthly_average_filter(monthly_avg, year, cities)
monthly_df = monthly_df.reset_index()
fig_heatmap = heatmaps(monthly_df, year, cities)
plot_trends = plot_city_trends(monthly_df, cities, year, ylim=[0, 75])


exceedance_days.to_csv(exceedance_out_path, index=False)
monthly_df.to_csv(monthly_out_path, index=False)
fig_heatmap.write_image(heatmap_out_path)
plot_trends.savefig(plot_trends_out_path, dpi=300)
