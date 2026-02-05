import json
from datetime import datetime
configfile: "config/task4.yaml"

years = config["years"]
cities = json.dumps(config["cities"])
timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
report_file = f"results/reports/report_task4_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.ipynb"


rule all:
    input:
        expand("data/years/{year}.csv", year=years),
        "data/all_data.csv",
        "data/monthly_average.csv",
        "data/daily_average.csv",
        expand("results/pm25/{year}/exceedance_days.csv", year=years),
        expand("results/pm25/{year}/daily_means.csv", year=years),
        expand("results/pm25/{year}/figures/heatmap.png", year=years),
        expand("results/pm25/{year}/figures/plot_city_trends.png", year=years),
        expand("results/literature/{year}/pubmed_papers.csv", year=years),
        expand("results/literature/summary_by_year.csv", year=years),
        expand("results/literature/{year}/top_journals.csv", year=years),
        expand("results/literature/papers_per_year.png", year=years),
        report_file


rule generate_year:
    output:
        "data/years/{year}.csv"
    shell:
        """ python scripts/generate_year.py --year {wildcards.year} --config config/task4.yaml --output {output} """


rule combined_years:
    input:
        years_files=expand("data/years/{year}.csv", year=years)
    output:
        all_data="data/all_data.csv",
        monthly="data/monthly_average.csv",
        daily="data/daily_average.csv"
    shell:
        """ python scripts/combined_years.py --input {input.years_files} --all_data {output.all_data} --monthly {output.monthly} --daily {output.daily} """



rule pm25_year:
    input:
        all_data="data/all_data.csv",
        monthly="data/monthly_average.csv",
        daily="data/daily_average.csv"
    output:
        exceed="results/pm25/{year}/exceedance_days.csv",
        daily="results/pm25/{year}/daily_means.csv",
        heatmap="results/pm25/{year}/figures/heatmap.png",
        city_trends="results/pm25/{year}/figures/plot_city_trends.png"
    shell:
        """ python scripts/pm25_year.py --year {wildcards.year} --config config/task4.yaml """


rule pubmed_year:
    output:
        pubmed_papers="results/literature/{year}/pubmed_papers.csv",
        journals="results/literature/{year}/top_journals.csv"
    shell:
        """ python scripts/pubmed_fetch.py --year {wildcards.year} --config config/task4.yaml """


rule pubmed_summary:
    input:
        expand("results/literature/{year}/pubmed_papers.csv", year=years),
    output:
        pubmed_summary="results/literature/summary_by_year.csv",
        papers_year="results/literature/papers_per_year.png"
    shell:
        """ python scripts/pubmed_summary.py --input {input} """


rule report_task4:
    input:
        pm25=expand("results/pm25/{year}/exceedance_days.csv", year=years),
        pubmed_papers=expand("results/literature/{year}/pubmed_papers.csv", year=years),
        pubmed_summary="results/literature/summary_by_year.csv",
        papers_year="results/literature/papers_per_year.png",
        journals=expand("results/literature/{year}/top_journals.csv", year=years),
        monthly="data/monthly_average.csv"
    output:
        report_file
    shell:
        """ python scripts/report_maker.py --timestamp {timestamp} --input {input.pm25} {input.pubmed_papers} {input.pubmed_summary} {input.papers_year} {input.journals} {input.monthly} --output {output} --config config/task4.yaml """


