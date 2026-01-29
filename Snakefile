import json
from datetime import datetime
configfile: "config/task4.yaml"

years = config["years"]
cities = json.dumps(config["cities"])
timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
report_file = f"results/report_task4_{timestamp}.ipynb"


rule all:
    input:
        expand("results/data/years/{year}.csv", year=years),
        "results/data/all_data.csv",
        "results/data/monthly_average.csv",
        "results/data/daily_average.csv",
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
        "results/data/years/{year}.csv"
    log:
        "logs/generate_year_{year}.log"
    shell:
        """ python generate_year.py --year {wildcards.year} --output {output} > {log} 2>&1 """


rule combined_years:
    input:
        expand("results/data/years/year={year}.csv", year=years)
    output:
        "results/data/all_data.csv",
        "results/data/monthly_average.csv",
        "results/data/daily_average.csv"
    shell:
        """ python combined_years.py --input {input} """



rule pm25_year:
    output:
        exceed="results/pm25/{year}/exceedance_days.csv",
        month="results/pm25/{year}/daily_means.csv",
        heatmap="results/pm25/{year}/figures/heatmap.png",
        city_trends="results/pm25/{year}/figures/plot_city_trends.png"
    log:
        "logs/pm25_year_{year}.log"
    shell:
        """ python scripts/pm25_year.py --year {wildcards.year} --config config/task4.yaml > {log} 2>&1 """


rule pubmed_year:
    output:
        pubmed_papers="results/literature/{year}/pubmed_papers.csv",
        journals="results/literature/{year}/top_journals.csv"
    log:
        "logs/pubmed_year_{year}.log"
    shell:
        """ python scripts/pubmed_fetch.py --year {wildcards.year} --config config/task4.yaml > {log} 2>&1 """


rule pubmed_summary:
    input:
        expand("results/literature/{year}/pubmed_papers.csv", year=years),
    output:
        pubmed_summary="results/literature/summary_by_year.csv",
        papers_year="results/literature/papers_per_year.png"
    shell:
        """ python scripts/pubmed_summary --config config/task4.yaml """


rule report_task4:
    input:
        pm25=expand("results/pm25/{year}/exceedance_days.csv", year=years),
        pubmed_papers=expand("results/literature/{year}/pubmed_papers.csv", year=years),
        pubmed_summary="results/literature/summary_by_year.csv",
        papers_year="results/literature/papers_per_year.png",
        journals=expand("results/literature/{year}/top_journals.csv", year=years),
        monthly="results/data/monthly_average.csv"
    output:
        report_file
    params:
        timestamp=lambda wildcards:"{timestamp}"
    shell:
        """ python scripts/report_maker.py --timestamp {params.timestamp} --input {input} --config config/task4.yaml """


