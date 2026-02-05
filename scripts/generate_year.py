from load_data import load_data
import argparse
import os
import yaml


parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--config", type=str, required=True)
args = parser.parse_args()

year = args.year
with open(args.config) as f:
    config = yaml.safe_load(f)
cities = config["cities"]
city_aliases = config["city_aliases"]

os.makedirs(os.path.dirname(args.output), exist_ok=True)

data = load_data(year, cities, city_aliases)
data.to_csv(args.output, index=False)