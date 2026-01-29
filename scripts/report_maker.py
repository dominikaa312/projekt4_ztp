import os
import argparse
import yaml
import nbformat as nbf
import pandas as pd



parser = argparse.ArgumentParser()
parser.add_argument("--timestamp", required=True)
parser.add_argument("--input", type=str, required=True)
parser.add_argument("--config", type=str, required=True)
args = parser.parse_args()

with open(args.config) as f:
    config = yaml.safe_load(f)
years = config['years']
input_files = args.input.split()
timestamp = args.timestamp.strftime("%Y-%m-%d_%H-%M-%S")



scripts_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(scripts_dir)
papers_fig_path = os.path.join(base_dir, 'results', 'literature', 'papers_per_year.png')

report_out_path = os.path.join("results", f"report_task4_{timestamp}.ipynb")



exceedance_files = [f for f in input_files if "exceedance_days.csv" in f]
dfs = [pd.read_csv(f) for f in exceedance_files]
all_exceedance = pd.concat(dfs, ignore_index=True)
city_total_exceedance = (all_exceedance.groupby("city", as_index=False)
                        .agg(total_days_exceeded=("days_exceeded", "sum"))
                        .sort_values("total_days_exceeded", ascending=False))


journals_files = [f for f in input_files if "top_journals.csv" in f]
dfs = [pd.read_csv(f) for f in journals_files]
all_journals = pd.concat(dfs, ignore_index=True)
top_journals_all_time = (all_journals.groupby("journal", as_index=False)
                        .agg(total_count=("count", "sum"))
                        .sort_values("total_count", ascending=False)
                        .head(5))


monthly = [f for f in input_files if "monthly_average.csv" in f]
monthly = monthly[0]
monthly_average = pd.read_csv(monthly)


pubmed_files = [f for f in input_files if "pubmed_papers.csv" in f]
dfs = [pd.read_csv(f) for f in pubmed_files]
all_titles = pd.concat(dfs, ignore_index=True)
titles = (all_titles.sort_values("title").head(5).reset_index(drop=True))
titles[" "] = titles.index + 1
titles = titles[[" ", "Title"]]
titles_table = titles.to_markdown(index=False)


pubmed_summary = [f for f in input_files if "pubmed_summary.csv" in f]
pubmed_summary = pubmed_summary[0]
summary = pd.read_csv(pubmed_summary)



nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell(f"## Raport\n### Lata: {years}"))

nb.cells.append(nbf.v4.new_markdown_cell(f"#### Liczba dni (w danej stacji przez wszystkie lata), w których została przekroczona dobowa norma stężenia PM2.5, czyli 15 µg/m³"))

nb.cells.append(nbf.v4.new_markdown_cell(city_total_exceedance.to_markdown(index=False)))

nb.cells.append(nbf.v4.new_markdown_cell(f"#### Średnie miesięczne w danych miastach"))

nb.cells.append(nbf.v4.new_markdown_cell(monthly_average.round(3).to_markdown(index=False)))

nb.cells.append(nbf.v4.new_markdown_cell(f"#### Trend liczby publikacji w czasie"))

nb.cells.append(nbf.v4.new_markdown_cell(summary.to_markdown(index=False)))

nb.cells.append(nbf.v4.new_code_cell("from IPython.display import Image, display\n\n" "display(Image(filename='" + papers_fig_path + "'))"))

nb.cells.append(nbf.v4.new_markdown_cell(f"#### Najpopularniejsze czasopisma"))

nb.cells.append(nbf.v4.new_markdown_cell(top_journals_all_time.to_markdown(index=False)))

nb.cells.append(nbf.v4.new_markdown_cell(f"#### Przykładowe artykuły\n\n" + titles_table))



with open(report_out_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)