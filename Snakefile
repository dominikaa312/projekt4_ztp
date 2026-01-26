import json
configfile: "config/task4.yaml"

years = config["years"]
cities = json.dumps(config["cities"])


rule all:
    input:
        expand("results/pm25/{year}/exceedance_days.csv", year=years),
        expand("results/pm25/{year}/monthly_average.csv", year=years),
        expand("results/pm25/{year}/figures/heatmap.png", year=years),
        expand("results/pm25/{year}/figures/plot_city_trends.png", year=years),
        expand("results/literature/{year}/pubmed_papers.csv", year=years),
        expand("results/literature/{year}/summary_by_year.csv", year=years),
        expand("results/literature/{year}/top_journals.csv", year=years),
        expand("results/literature/{year}/papers_per_year.png", year=years),
        "results/report_task4.md"


rule pm25_year:
    output:
        exceed="results/pm25/{year}/exceedance_days.csv",
        month="results/pm25/{year}/monthly_average.csv",
        heatmap="results/pm25/{year}/figures/heatmap.png",
        city_trends="results/pm25/{year}/figures/plot_city_trends.png"
    params:
        year="{year}",
        cities=cities
    shell:
        """ python scripts/pm25_year.py --year {params.year} --cities {params.cities} --config config/task4.yaml """


rule pubmed_year:
    output:
        pubmed_papers="results/literature/{year}/pubmed_papers.csv",
        summary="results/literature/{year}/summary_by_year.csv",
        journals="results/literature/{year}/top_journals.csv",
        papers_year="results/literature/{year}/papers_per_year.png"
    params:
        year="{year}"
    shell:
        """ python scripts/pubmed_fetch.py --year {params.year} --config config/task4.yaml """

rule report_task4:
    input:
        pm25=expand("results/pm25/{year}/exceedance_days.csv", year=years),
        literature=expand("results/literature/{year}/pubmed_papers.csv", year=years)
    output:
        "results/report_task4.md"
    shell:
        """ python scripts/NAZWA_PLIKU --config config/task4.yaml """ # WPISAĆ NAZWĘ PLIKU!


