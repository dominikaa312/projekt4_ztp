from load_data import load_data
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
year = args.year

data = load_data(year)
data.to_csv(args.output, index=False)