import os
import argparse
import yaml
from datetime import datetime
import nbformat as nbf
from IPython.display import Image, display



def parser_timestamp(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

parser = argparse.ArgumentParser()
parser.add_argument("--timestamp", type=parser_timestamp, required=True)
parser.add_argument("--config", type=str, required=True)
args = parser.parse_args()

with open(args.config) as f:
    config = yaml.safe_load(f)
years = config['years']
timestamp = args.timestamp



scripts_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(scripts_dir)
papers_fig_path = os.path.join(base_dir, 'results', 'literature', 'papers_per_year.png')

report_out_path = os.path.join("results", f"report_task4_{timestamp}.ipynb")



nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell(f"## Raport\n### Lata: {years}"))

nb.cells.append(nbf.v4.new_markdown_cell(f"#### Trend liczby publikacji w czasie"))

nb.cells.append(nbf.v4.new_code_cell(f"display(Image(filename={papers_fig_path}))"))