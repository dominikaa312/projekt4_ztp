import pandas as pd
import argparse
from pubmed_functions import papers_count_per_year, plot_per_year
import os


parser = argparse.ArgumentParser()
parser.add_argument("--input", nargs="+", required=True)
args = parser.parse_args()

dataframes = [pd.read_csv(df) for df in args.input]
df_all = pd.concat(dataframes, ignore_index=True)

summary = papers_count_per_year(df_all)
summary_out_path = os.path.join("results", "literature", "summary_by_year.csv")
summary.to_csv(summary_out_path, index=False)

plot = plot_per_year(summary)
plot_out_path = os.path.join("results", "literature", "papers_per_year.png")
plot.savefig(plot_out_path, dpi=300)