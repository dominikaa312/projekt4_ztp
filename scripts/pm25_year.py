from compute_averages import count_days_over_threshold
from visualizations import *
import pandas as pd
import os
import argparse
import yaml



parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--config", type=str, required=True)
args = parser.parse_args()

year = args.year
with open(args.config) as f:
    config = yaml.safe_load(f)
cities = config["cities"]
city_aliases = config["city_aliases"]



scripts_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(scripts_dir)

data_path = os.path.join(base_dir, "data", "all_data.csv")
data = pd.read_csv(data_path)

monthly_avg_path = os.path.join(base_dir, "data", "monthly_average.csv")
monthly_avg = pd.read_csv(monthly_avg_path)

daily_avg_path = os.path.join(base_dir, "data", "daily_average.csv")
daily_avg = pd.read_csv(daily_avg_path)



exceedance_out_path = os.path.join("results", "pm25", str(year), "exceedance_days.csv")
os.makedirs(os.path.dirname(exceedance_out_path), exist_ok=True)
exceedance_days = count_days_over_threshold(data, config["pm25"]["norm_limit"], year, cities, city_aliases)
exceedance_days.to_csv(exceedance_out_path, index=False)


heatmap_out_path = os.path.join("results", "pm25", str(year), "figures", "heatmap.png")
os.makedirs(os.path.dirname(heatmap_out_path), exist_ok=True)
fig_heatmap = heatmaps(monthly_avg, year, cities, city_aliases)
fig_heatmap.write_image(heatmap_out_path)

plot_trends_out_path = os.path.join("results", "pm25", str(year), "figures", "plot_city_trends.png")
os.makedirs(os.path.dirname(plot_trends_out_path), exist_ok=True)
plot_trends = plot_city_trends(monthly_avg, cities, year, city_aliases, ylim=[0, 75])
plot_trends.savefig(plot_trends_out_path, dpi=300)


daily_avg_year = daily_avg[daily_avg['year'] == year]
selected_cols = ['year', 'month', 'day']
for city in cities:
    if city in daily_avg.columns:
        selected_cols.append(city)
    elif city_aliases and city in city_aliases:
        for alias in city_aliases[city]:
            if alias in daily_avg.columns:
                selected_cols.append(alias)
                break
daily_avg_filtered = daily_avg_year[selected_cols]

daily_means_out_path = os.path.join("results", "pm25", str(year), "daily_means.csv")
os.makedirs(os.path.dirname(daily_means_out_path), exist_ok=True)
daily_avg_filtered.to_csv(daily_means_out_path, index=False)

print(f"Finished PM2.5 for year {year}, results saved to {exceedance_out_path} and {daily_means_out_path}")

