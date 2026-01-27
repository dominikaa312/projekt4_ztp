import os
import argparse
import yaml
from Bio import Entrez, Medline
from pubmed_functions import *



parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--config", type=str, required=True)
args = parser.parse_args()

year = args.year
with open(args.config) as f:
    config = yaml.safe_load(f)
Entrez.email = config['pubmed']['entrez_email']



query = build_query(config, year)
handle = Entrez.esearch(db="pubmed", term=query, retmax=config["pubmed"]["retmax"])
record = Entrez.read(handle)
pmids = record["IdList"]
handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="medline", retmode="text")
records = list(Medline.parse(handle))
pubmed_papers_df = record_to_df(records)

pubmed_papers_out_path = os.path.join("results", "literature", str(year), "pubmed_papers.csv")
os.makedirs(os.path.dirname(pubmed_papers_out_path), exist_ok=True)
pubmed_papers_df.to_csv(pubmed_papers_out_path, index=False)

year_count_out_path = os.path.join("results", "literature", "summary_by_year.csv")
year_count = papers_count_per_year(pubmed_papers_df)
year_count.to_csv(year_count_out_path, index=False)

fig_year_out_path = os.path.join("results", "literature", "papers_per_year.png")
fig_year = plot_per_year(year_count)
fig_year.savefig(fig_year_out_path, dpi=300)

top_journals_out_path = os.path.join("results", "literature", str(year), "top_journals.csv")
top = top_journals(pubmed_papers_df)
top.to_csv(top_journals_out_path, index=False)